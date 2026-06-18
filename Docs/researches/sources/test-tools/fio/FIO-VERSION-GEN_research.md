# `sources/test-tools/fio/FIO-VERSION-GEN`

Purpose: Shell script that derives and writes fio’s build version into `FIO-VERSION-FILE`.

Important variables and behavior: `GVF=FIO-VERSION-FILE`; default version is `fio-3.42`. Version resolution checks a release `version` file first, then `git describe --match "fio-[0-9]*" --abbrev=4 HEAD`, appending `-dirty` if the index differs from HEAD, and finally falls back to the default. It strips a leading `v` with `expr`, compares against the current generated file, and rewrites only when changed.

Control flow: The Makefile target `FIO-VERSION-FILE` invokes this script before compiling sources that need `FIO_VERSION`. It refreshes git index state before dirty detection.

State and persistence: Writes `FIO-VERSION-FILE` in the build directory and emits the selected version to stderr when it changes.

Dependencies and integration: Depends on POSIX shell, `git`, `expr`, `sed`, and Makefile inclusion of `FIO-VERSION-FILE`.

Risks and test signals: Builds outside git rely on `version` or the default. Dirty detection can mark generated or untracked-insensitive changes depending on git index behavior. Tests should run from release tarballs, clean git trees, dirty trees, and non-git source copies.
