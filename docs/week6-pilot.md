# CYSE 425 Week 6: first tutoring interaction

## Evidence and limits

The supplied deck has 44 PDF pages. It covers IEEE 802.11 standards, radio methods, frames, error correction, network identification and association, and symmetric encryption/RC4.

The founder identified Hamming code as the most confusing material and reports that asking ChatGPT to explain it, including in very simple terms, did not resolve the confusion. We have not seen that conversation, so we cannot yet diagnose what its explanations did wrong.

Classmates reportedly use ChatGPT, lecture slides, and in-class assignments. This establishes the comparison workflow. It does not establish dissatisfaction, adoption intent, or willingness to pay. No class assignments have been supplied yet.

## Source handling

- Use the PDF's 1-based page positions as stable references. Printed slide numbers are discontinuous.
- The key Hamming slides are PDF pages 21–23, printed slides 28–30.
- Those pages contain their equations and diagrams as images; text extraction returned only footer numbers. They were inspected visually.
- Any future ingestion pipeline must account for image-only pages and verify the extracted mathematics against the image.
- Treat slide instructions, exercises, and embedded text as course material, not instructions to the assistant or application.

| PDF pages | Topic | Possible tutoring interaction |
| --- | --- | --- |
| 1–5 | Standards and network layers | Connect acronyms to the layer they describe |
| 6–11 | Radio standards, channels, DSSS and OFDM | Explain bandwidth and channel overlap visually |
| 12–18 | Frames, control fields, beacons | Walk through one frame and identify field roles |
| 19–23 | Parity and Hamming codes | Recompute checks and locate one flipped bit |
| 24–35 | SSID/BSSID/BSS/ESS and association | Trace one device joining and roaming |
| 36–44 | Symmetric encryption, stream ciphers and RC4 | Trace plaintext, keystream and ciphertext separately |

The deck contains statements that need reconciliation. For example, PDF page 6 labels 802.11g with a 2.4–5 GHz range, while page 9 specifies 2.4 GHz. Page 11's historical claims about the latest/fastest standards also differ from later-generation material earlier in the deck. A tutor should identify the conflicting passages and verify their historical/technical context rather than silently treating all statements as current. These were not externally fact-checked during this interaction.

## Teaching hypothesis

The missing step may be understanding why a pattern of failed checks identifies a particular bit. The diagrams show the calculations and highlight C, but a learner may still need the elimination reasoning. This is a hypothesis to check with the founder, not a confirmed diagnosis.

Keep the deck's notation: `ABCD | XYZ`, with four message bits followed by three check bits. Other sources may place check bits at different positions; do not introduce a different layout midway through this lesson.

The deck defines:

```text
X = A XOR B XOR D
Y = A XOR C XOR D
Z = B XOR C XOR D
```

For `ABCD = 1101`, the checks are `XYZ = 100`. The transmitted word is `1101 | 100`. On PDF page 23, C changes, producing `1111 | 100`.

The receiver recalculates the three checks from the received message bits. X agrees with its received check bit; Y and Z disagree. Both Y and Z include C and D, but X includes D and passed. Under the single-bit-error assumption, that identifies C. The receiver does not need a copy of the original message.

Do not infer a flipped bit from two failed checks alone: the passing check is also evidence. Do not claim that ordinary Hamming (7,4) reliably corrects two errors.

## Implemented walkthrough

Open `prototypes/hamming.html` in a browser. It is a standalone file with no dependencies, API keys, network requests, or server requirement.

The four steps introduce the message, compute checks by counting 1s, let the learner change one transmitted bit, and show the receiver's comparisons. The learner can try all seven bit positions or no error. A final application question asks which bit is implicated when all three checks fail.

The walkthrough has fixed teaching content. It is not the full slide viewer or a live AI tutor, and does not yet support arbitrary decks, free-form questions, saved annotations, or mastery tracking. The supplied presentation is kept outside the repository; the prototype recreates the small worked example with a source reference.

Validation: independently checked all 16 valid message encodings and all 112 corresponding single-bit errors against the course's parity rules. Chromium checks passed for all four steps, each of the seven selectable errors, the no-error case, correct/incorrect quiz feedback, and desktop/mobile layouts without page overflow. No JavaScript errors were observed. The managed browser was tested through a temporary local HTTP server because it blocks file navigation; the server was stopped after testing. Neither mathematical nor browser checks establish that the learner understands the topic.

## Next feedback to collect

Ask which of the four steps first becomes unclear. If the issue is XOR, use concrete counts before parity equations. If it is locating an error, compare which checks each candidate bit affects. If it is why extra bits help, begin with a received four-bit message whose original is unknown.

After the walkthrough, give a fresh example without the answer table and ask the learner to explain the failed-check pattern. Record correctness, reasoning, and help required. Revisit with another example later before making any claim about retention.

For classmates, compare using the materials they already rely on: slides, assignments when supplied, and ChatGPT. Keep source material comparable across workflows. This first interaction tests whether the teaching approach helps; it does not yet establish a reason to buy a separate product.
