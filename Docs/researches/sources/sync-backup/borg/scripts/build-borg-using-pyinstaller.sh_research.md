# sources/sync-backup/borg/scripts/build-borg-using-pyinstaller.sh

Purpose: Builds a one-file Borg binary using PyInstaller and a checked-in spec file.

Important APIs/types/functions: Shell variables are `OUTPUT_DIR=dist/binary` and `SPEC_FILE=scripts/borg.exe.spec`. External API is `pyinstaller -y --clean --distpath="$OUTPUT_DIR" "$SPEC_FILE"`.

Control flow: `set -eu` enables fail-fast behavior. The script creates the output directory, invokes PyInstaller with overwrite and clean cache behavior, and prints `dist/binary/borg.exe`.

State and persistence: Writes distribution output under `dist/binary` and PyInstaller build/cache artifacts. Existing output can be overwritten due to `-y`.

Dependencies and integration points: Requires PyInstaller, the spec file, and a Python environment containing Borg and native dependencies. Used as an alternative binary packaging path to Nuitka.

Risks: Build correctness is highly dependent on the spec file, hidden imports, and native library collection. `--clean` increases build time but reduces stale-cache risk.

Test signals: Run script, execute `dist/binary/borg.exe -V`, and smoke-test commands requiring crypto, compression, repository backends, and optional FUSE/backend features intended for the binary.
