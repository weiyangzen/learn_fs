# sources/storage-engines/wiredtiger/tools/tsan_playground/collect_warnings.sh

Purpose: runs all built TSAN playground executables and summarizes ThreadSanitizer warnings for each implementation variant.

Important APIs and control flow: assumes it is run from a build folder, scans `./tools/tsan_playground/tsan_playground_*`, resolves each executable path, runs it with a five-second `timeout`, extracts the `Implementation:` label and `SUMMARY: ThreadSanitizer:` lines, reports timeout/completed/error status and exit code, then prints warnings or `No warnings detected`.

State and persistence behavior: read-only over built executables; no files are written.

Dependencies and integration points: depends on Bash, `realpath`, `timeout`, `grep`, and the CMake-built playground executables. It is the runtime companion to `CMakeLists.txt`.

Risks: the hard-coded build-relative folder must match CMake output layout. Capturing all output into a shell variable may be large for verbose TSAN runs. It only reports summary lines, not full race traces. Five seconds may be too short on slow sanitizer builds.

Test signals: output gives per-executable labels and TSAN summary lines; the dummy variant should warn, while expected-safe atomic variants ideally do not.
