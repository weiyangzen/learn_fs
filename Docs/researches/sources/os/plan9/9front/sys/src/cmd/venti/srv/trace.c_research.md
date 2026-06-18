# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/trace.c

`trace.c` defines trace category strings and the `trace()` helper for Venti logging. When `ventilogging` is enabled, trace messages are formatted with thread names and written both to the specific category log and the aggregate `all` log as HTML snippets.

`traceinit()` and `settrace()` are stubs in this version, so runtime category filtering is not implemented here. The categories are still used throughout disk, lump, block, process, work, quiet, and RPC paths.
