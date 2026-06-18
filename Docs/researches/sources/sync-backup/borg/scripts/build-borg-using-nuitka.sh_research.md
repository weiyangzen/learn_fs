# sources/sync-backup/borg/scripts/build-borg-using-nuitka.sh

Purpose: Builds a one-file Borg binary using Nuitka into `dist/binary/borg-nuitka.exe`.

Important APIs/types/functions: Shell variables are `OUTPUT_DIR`, `OUTPUT_FILENAME`, and `SRC_DIR`. Main external API is `python -m nuitka` with `--mode=onefile`, `--assume-yes-for-downloads`, package includes for `borg`, `borghash`, `borgstore`, and `cffi`, and `PYTHONPATH=src`.

Control flow: `set -eu` aborts on unset variables or command failures. The script creates the output directory, runs Nuitka against `src/borg`, then prints the generated path.

State and persistence: Writes build artifacts under `dist/binary`. Nuitka may create caches/intermediate files and may download toolchain components due to `--assume-yes-for-downloads`.

Dependencies and integration points: Requires Nuitka, a usable Python environment with Borg dependencies, local `src` tree, and compiler/toolchain support. It complements PyInstaller packaging.

Risks: Output filename uses `.exe` even on non-Windows, which can confuse downstream tooling. Unquoted `mkdir -p $OUTPUT_DIR` is safe for current value but brittle for spaces. Including CFFI is explicitly required to avoid argon2 runtime import failures.

Test signals: Run the script in a clean environment, execute `dist/binary/borg-nuitka.exe -V`, and smoke-test encrypted repository operations to catch missing packages/native modules.
