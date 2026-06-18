# sources/sync-backup/casync/tools/oss-fuzz.sh

Purpose: build script for producing OSS-Fuzz-compatible casync fuzzing artifacts.

Important APIs/types/functions: configures clang/sanitizer flags, detects clang runtime library path, sets `WORK`/`OUT`, configures Meson with `oss-fuzz` or `llvm-fuzz`, disables some optional libs/manpages, runs `ninja fuzzers`, packages seed corpora, and moves `fuzz-*` executables to `$OUT`.

Control flow/state: deletes/recreates `$WORK/build`, writes artifacts under `$OUT`, and zips corpus directories named after fuzzers.

Dependencies/integration: used by OSS-Fuzz infrastructure and local sanitizer builds; depends on Meson, Ninja, clang, zip, and fuzz Meson targets.

Risks/test signals: sanitizer flag or clang library path drift can break fuzz builds. Disabling compression libraries narrows fuzz coverage unless separate jobs enable them.

Source research group: `subset-b-009122`.
