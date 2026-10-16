import AppKit
import CoreGraphics
import WebKit
import ScreenCaptureKit
import Vision

// A local source-built accessory app. No browser extension, account, or paid SDK.
final class CompanionPanel: NSPanel {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { false }
}

final class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate, WKScriptMessageHandler, WKNavigationDelegate {
    private var item: NSStatusItem!
    private var panel: CompanionPanel!
    private var web: WKWebView!
    private var launcher: Process?
    private var logHandle: FileHandle?
    private var timer: Timer?
    private var readiness: Timer?
    private var following = false
    private var capturing = false
    private var generation = 0
    private var lastPID: pid_t?
    private var activationObserver: NSObjectProtocol?
    private var root = URL(fileURLWithPath: "/")
    private let origin = URL(string: "http://127.0.0.1:8000")!

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        item = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        item.button?.image = NSImage(systemSymbolName: "book.closed", accessibilityDescription: "StudyBuddy")
        item.button?.toolTip = "StudyBuddy · Paused"
        item.button?.target = self
        item.button?.action = #selector(togglePanel)
        item.button?.sendAction(on: [.leftMouseUp, .rightMouseUp])
        let config = WKWebViewConfiguration()
        config.userContentController.add(self, name: "studybuddy")
        web = WKWebView(frame: .zero, configuration: config)
        web.navigationDelegate = self
        panel = CompanionPanel(contentRect: NSRect(x: 0, y: 0, width: 430, height: 700),
                               styleMask: [.titled, .closable, .resizable, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.title = "StudyBuddy"
        panel.minSize = NSSize(width: 360, height: 440)
        panel.level = .floating
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        panel.hidesOnDeactivate = false
        panel.isReleasedWhenClosed = false
        panel.delegate = self
        panel.contentView = web
        panel.setFrameAutosaveName("StudyBuddyCompanion")
        if let screen = NSScreen.main {
            let frame = screen.visibleFrame
            panel.setFrameOrigin(NSPoint(x: frame.maxX - 450, y: frame.maxY - 720))
        }
        activationObserver = NSWorkspace.shared.notificationCenter.addObserver(forName: NSWorkspace.didActivateApplicationNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self = self, self.following,
                  NSWorkspace.shared.frontmostApplication?.processIdentifier != ProcessInfo.processInfo.processIdentifier else { return }
            self.generation += 1 // Drop an OCR result from the previous application.
            self.emit(["type": "changing", "message": "Following your active window…"])
            self.capture()
        }
        startServices()
        showPanel()
    }

    private func startServices() {
        guard let location = Bundle.main.object(forInfoDictionaryKey: "StudyBuddySourceRoot") as? String else {
            showStartup("The source-folder location is missing. Rebuild the Mac app."); return
        }
        root = URL(fileURLWithPath: location)
        let python = root.appendingPathComponent(".venv/bin/python")
        guard FileManager.default.isExecutableFile(atPath: python.path),
              FileManager.default.fileExists(atPath: root.appendingPathComponent("dist/index.html").path) else {
            showStartup("Run bash scripts/setup.sh in the source folder, then reopen StudyBuddy."); return
        }
        let process = Process()
        process.executableURL = python
        process.arguments = ["scripts/run.py", "--no-browser"]
        // A missing model still permits testing the companion shell and PDF notes.
        if !FileManager.default.fileExists(atPath: root.appendingPathComponent(".studybuddy/models/model.json").path) {
            process.arguments?.append("--workspace-only")
        }
        process.currentDirectoryURL = root
        var environment = ProcessInfo.processInfo.environment
        environment["STUDYBUDDY_PORT"] = "8000"
        environment["PATH"] = "/opt/homebrew/bin:/opt/homebrew/opt/node@22/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:" + (environment["PATH"] ?? "")
        process.environment = environment
        let logs = root.appendingPathComponent(".studybuddy/logs")
        do {
            try FileManager.default.createDirectory(at: logs, withIntermediateDirectories: true)
            let log = logs.appendingPathComponent("native.log")
            if !FileManager.default.fileExists(atPath: log.path) { FileManager.default.createFile(atPath: log.path, contents: nil) }
            logHandle = try FileHandle(forWritingTo: log)
            logHandle?.seekToEndOfFile()
            process.standardOutput = logHandle
            process.standardError = logHandle
            try process.run()
            launcher = process
        } catch { showStartup("Startup failed. See .studybuddy/logs/native.log in the source folder."); return }
        showStartup("Starting your local study companion… The first model load may take a few minutes.")
        var attempts = 0
        readiness = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] timer in
            guard let self = self else { timer.invalidate(); return }
            attempts += 1
            if !process.isRunning || attempts > 220 {
                timer.invalidate()
                self.showStartup("Could not start. Close any earlier StudyBuddy session and check .studybuddy/logs/native.log in the source folder.")
                return
            }
            var request = URLRequest(url: self.origin.appendingPathComponent("api/health"))
            request.timeoutInterval = 2
            URLSession.shared.dataTask(with: request) { data, response, _ in
                guard (response as? HTTPURLResponse)?.statusCode == 200,
                      let data = data,
                      let value = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any],
                      value["status"] as? String == "ok" else { return }
                DispatchQueue.main.async {
                    guard timer.isValid, process.isRunning else { return }
                    timer.invalidate()
                    self.web.load(URLRequest(url: URL(string: "/?companion=1", relativeTo: self.origin)!))
                }
            }.resume()
        }
    }

    private func showStartup(_ text: String) {
        web.loadHTMLString("<html><meta name='viewport' content='width=device-width'><body style='font:16px -apple-system;padding:30px;background:#f7f8f5;color:#23362d'><h2>StudyBuddy</h2><p>\(text)</p><p>Right-click the menu-bar icon to quit.</p></body></html>", baseURL: nil)
    }

    @objc private func togglePanel() {
        if NSApp.currentEvent?.type == .rightMouseUp {
            let menu = NSMenu()
            let show = menu.addItem(withTitle: "Show StudyBuddy", action: #selector(showPanel), keyEquivalent: "")
            show.target = self
            let pause = menu.addItem(withTitle: "Pause study mode", action: #selector(pauseFollowing), keyEquivalent: "")
            pause.target = self; pause.isEnabled = following
            menu.addItem(.separator())
            let quit = menu.addItem(withTitle: "Quit StudyBuddy", action: #selector(quit), keyEquivalent: "q")
            quit.target = self
            item.menu = menu
            item.button?.performClick(nil)
            item.menu = nil
        } else if panel.isVisible {
            pauseFollowing(); panel.orderOut(nil)
        } else { showPanel() }
    }

    @objc private func showPanel() { panel.orderFrontRegardless() }
    @objc private func quit() { NSApp.terminate(nil) }
    func windowShouldClose(_ sender: NSWindow) -> Bool { pauseFollowing(); panel.orderOut(nil); return false }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.frameInfo.isMainFrame,
              message.frameInfo.securityOrigin.host == "127.0.0.1",
              message.frameInfo.securityOrigin.protocol == "http",
              message.frameInfo.securityOrigin.port == 8000,
              let body = message.body as? [String: Any], let action = body["action"] as? String else { return }
        switch action {
        case "start": startFollowing()
        case "pause": pauseFollowing()
        case "hide": pauseFollowing(); panel.orderOut(nil)
        case "ready": emit(["type": "status", "active": following, "message": following ? "Following your active window" : "Study mode is paused"])
        default: break
        }
    }

    private func startFollowing() {
        guard !following else { return }
        guard CGPreflightScreenCaptureAccess() else {
            CGRequestScreenCaptureAccess()
            emit(["type": "status", "active": false, "message": "Allow StudyBuddy in System Settings → Privacy & Security → Screen Recording, then reopen it if macOS asks and turn on study mode."])
            return
        }
        following = true; generation += 1
        item.button?.image = NSImage(systemSymbolName: "book.closed.fill", accessibilityDescription: "StudyBuddy study mode on")
        item.button?.toolTip = "StudyBuddy · Study mode on"
        emit(["type": "status", "active": true, "message": "Following your active window…"])
        timer = Timer.scheduledTimer(withTimeInterval: 3, repeats: true) { [weak self] _ in self?.capture() }
        capture()
    }

    @objc private func pauseFollowing() {
        following = false; generation += 1; lastPID = nil
        timer?.invalidate(); timer = nil
        item.button?.image = NSImage(systemSymbolName: "book.closed", accessibilityDescription: "StudyBuddy paused")
        item.button?.toolTip = "StudyBuddy · Paused"
        emit(["type": "status", "active": false, "message": "Paused · screen capture stopped"])
    }

    private func emit(_ value: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: value), let json = String(data: data, encoding: .utf8) else { return }
        // JSON serialization prevents screen text from becoming executable JS.
        web.evaluateJavaScript("window.dispatchEvent(new CustomEvent('studybuddy:screen', {detail: \(json)}));", completionHandler: nil)
    }

    private func capture() {
        guard following, !capturing else { return }
        let ownPID = ProcessInfo.processInfo.processIdentifier
        let active = NSWorkspace.shared.frontmostApplication
        let pid: pid_t
        if let active = active, active.processIdentifier != ownPID { pid = active.processIdentifier; lastPID = pid }
        else if let previous = lastPID { pid = previous }
        else { emit(["type": "changing", "message": "Open your lecture, Canvas, video, or another study window."]); return }
        // Window-server order identifies the frontmost ordinary window. Capture
        // that one window, never the whole display or StudyBuddy's own panel.
        let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
        guard let info = windows.first(where: {
            ($0[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value == pid &&
            ($0[kCGWindowLayer as String] as? NSNumber)?.intValue == 0
        }), let windowID = info[kCGWindowNumber as String] as? NSNumber else {
            emit(["type": "changing", "message": "No readable study window is visible."]); return
        }
        capturing = true
        let epoch = generation
        SCShareableContent.getExcludingDesktopWindows(true, onScreenWindowsOnly: true) { [weak self] content, error in
            DispatchQueue.main.async {
                guard let self = self else { return }
                guard self.following, self.generation == epoch else { self.capturing = false; return }
                guard error == nil, let window = content?.windows.first(where: { $0.windowID == windowID.uint32Value }), window.frame.width > 100, window.frame.height > 100 else {
                    self.capturing = false
                    self.emit(["type": "changing", "message": "This window is unavailable. StudyBuddy will try the next visible window."]); return
                }
                let filter = SCContentFilter(desktopIndependentWindow: window)
                let configuration = SCStreamConfiguration()
                let scale = min(1.5, 1440 / max(window.frame.width, window.frame.height))
                configuration.width = max(1, Int(window.frame.width * scale))
                configuration.height = max(1, Int(window.frame.height * scale))
                configuration.showsCursor = false
                let title = String((window.title ?? "Study window").prefix(500))
                let application = String((window.owningApplication?.applicationName ?? "Active app").prefix(200))
                SCScreenshotManager.captureImage(contentFilter: filter, configuration: configuration) { [weak self] image, error in
                    guard let image = image, error == nil else {
                        DispatchQueue.main.async {
                            guard let self = self else { return }; self.capturing = false
                            if self.following && self.generation == epoch { self.emit(["type": "changing", "message": "This window could not be read. Protected video or minimized windows may be unavailable."]) }
                        }; return
                    }
                    DispatchQueue.global(qos: .userInitiated).async {
                        let request = VNRecognizeTextRequest()
                        request.recognitionLevel = .accurate
                        request.recognitionLanguages = ["en-US"]
                        request.usesLanguageCorrection = false
                        try? VNImageRequestHandler(cgImage: image, options: [:]).perform([request])
                        let text = String((request.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n").prefix(24000))
                        let bitmap = NSBitmapImageRep(cgImage: image)
                        let jpeg = bitmap.representation(using: .jpeg, properties: [.compressionFactor: 0.72])
                        DispatchQueue.main.async {
                            guard let self = self else { return }; self.capturing = false
                            guard self.following, self.generation == epoch else { return }
                            guard let jpeg = jpeg, jpeg.count <= 2_000_000 else {
                                self.emit(["type": "changing", "message": "This window snapshot is unavailable. Try another view."]); return
                            }
                            self.emit(["type": "frame", "application": application, "title": title, "text": text,
                                       "image": "data:image/jpeg;base64," + jpeg.base64EncodedString(), "capturedAt": Date().timeIntervalSince1970 * 1000])
                        }
                    }
                }
            }
        }
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }
        if url.scheme == "about" || (url.scheme == "http" && url.host == "127.0.0.1" && url.port == 8000) {
            decisionHandler(.allow)
        } else { decisionHandler(.cancel) } // Course content cannot navigate a privileged web view elsewhere.
    }

    func applicationWillTerminate(_ notification: Notification) {
        pauseFollowing(); readiness?.invalidate()
        if let observer = activationObserver { NSWorkspace.shared.notificationCenter.removeObserver(observer) }
        if let process = launcher, process.isRunning { process.terminate(); process.waitUntilExit() }
        try? logHandle?.close()
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
