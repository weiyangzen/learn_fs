# File Research: sources/os/plan9/9front/sys/src/cmd/lp/lpdaemon.c

`lpdaemon` is a portable C inbound print daemon that accepts remote print protocol requests, stores received control/data files in temporary files, derives job metadata, and invokes local `lp`.

Supported flows:
- BSD/lpr-style control bytes for queue/status/kill/send operations.
- Control file records provide host (`H`) and user (`P`) metadata.
- Data files are acknowledged with NUL ACK bytes and read to temp files under platform-specific temp directories.
- `forklp()` builds and logs an `lp` command line, redirects input from a temp data file, and waits for the child.
- Alarms guard protocol stalls and log debug state.

It contains compatibility sections for Plan 9, V10, SYSV, and BSD. Notable fragility includes fixed argument/data arrays, temp-file naming by pid/index, limited varargs logging style, and no explicit bound check on the `datafd[400]` job count.
