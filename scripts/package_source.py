"""Create a Mac source handoff without course files, local data, weights, or secrets."""
import argparse
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = ['README.md', 'AGENTS.md', '.gitignore', 'StudyBuddy.command', 'index.html',
              'package.json', 'package-lock.json', 'requirements.txt', 'requirements.lock',
              'tsconfig.json', 'vite.config.ts']
SOURCE_DIRECTORIES = ['src', 'server', 'scripts', 'tests', 'docs', 'evaluations', 'native']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Choose a new archive filename; previous handoffs are preserved.')
    files = [ROOT / name for name in ROOT_FILES]
    for directory in SOURCE_DIRECTORIES:
        files.extend(path for path in (ROOT / directory).rglob('*') if path.is_file()
                     and path.suffix not in ['.pyc', '.zip'] and '__pycache__' not in path.parts
                     and not path.is_symlink())
    files = sorted(set(files))
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = []
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name = path.relative_to(ROOT).as_posix()
            manifest.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}')
            archive.write(path, f'StudyBuddy/{name}')
        archive.writestr('StudyBuddy/SOURCE-MANIFEST.sha256', '\n'.join(manifest) + '\n')
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise SystemExit('Archive verification failed.')
    print(f'{output}: {len(files)} source/document files, {output.stat().st_size} bytes')
    print(f'SHA-256: {hashlib.sha256(output.read_bytes()).hexdigest()}')


if __name__ == '__main__':
    main()
