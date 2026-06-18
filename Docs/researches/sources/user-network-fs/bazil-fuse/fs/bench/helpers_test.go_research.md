<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/helpers_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/helpers_test.go

Purpose: benchmark package `TestMain` wiring for spawntest helper subprocesses.

Important APIs, types, and functions: declares global `helpers spawntest.Registry`; `TestMain` adds helper flags, parses flags, runs helper mode if selected, and then runs tests/benchmarks.

Control flow: helper subprocesses enter `helpers.RunIfNeeded` and do not return; normal benchmark processes call `m.Run`.

State and persistence behavior: process-wide command-line flags and helper registry state only.

Dependencies and integration points: required by benchmark helpers registered in other files.

Risks and test signals: missing `TestMain` would make helper spawning fail due to unknown flags or inactive helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/helpers_test.go -->
