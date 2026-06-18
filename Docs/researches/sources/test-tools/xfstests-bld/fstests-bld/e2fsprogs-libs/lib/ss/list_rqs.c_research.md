# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/list_rqs.c

## Purpose
`list_rqs.c` prints a formatted list of available ss requests through the configured pager.

## Important APIs, Types, and Functions
The public command handler is `ss_list_requests()`.

## Control Flow
It blocks SIGINT, starts a pager pipe with `ss_pager_create()`, writes a heading, walks all request tables and visible entries, formats command aliases with help strings, closes the pager stream, waits for the child when forking is enabled, and restores the signal handler.

## State, Persistence, Dependencies, Risks, and Test Signals
State is read from `ss_data.rqt_tables`. Dependencies include pager code, request flags, signal APIs, and stdio. Risks include formatting overflow assumptions around `BUFSIZ`, possible wait-for-any-child behavior, and signal restoration issues. Test signals are `?` or `list_requests` output in `test_ss` and hidden commands respecting `SS_OPT_DONT_LIST`.
