# sources/sync-backup/bup/dev/system-info

## Purpose
Prints OS, hardware, tool, filesystem, mount, identity, and cwd diagnostics for CI and failure debugging.

## Important APIs, Types, and Functions
Runs `uname -a`, platform-specific `/proc`/`sysctl`/`system_profiler`, `git --version`, `rsync --version`, optional `par2 -V`, `df -h`, `mount`, `id`, and `pwd`.

## Control Flow
Prints basic system info, branches by `OSTYPE`, enables shell tracing for command diagnostics, then runs tool/environment commands.

## State and Persistence Behavior
Read-only diagnostics.

## Dependencies and Integration Points
Called by Cirrus tasks before builds/tests.

## Risks and Test Signals
Risks are noisy logs and platform command availability. Signal is diagnostic output sufficient to debug CI environment differences.
