# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/common.h

This common header ties together Plan 9 mail constants, flag definitions, common helpers, folder operations, formatting hooks, and process helper types.

Key contents:
- Defines mailbox/path sizing constants and includes `sys.h` plus `<String.h>`.
- Defines mail flag bits `Fanswered`, `Fdeleted`, `Fdraft`, `Fflagged`, `Frecent`, `Fseen`, `Fstored`, and `Fields`.
- Declares flag helpers, auxiliary helpers, folder append/open helpers, RFC 2047 formatting install, and process/stream helpers.
- Defines `stream` and `process` abstractions around pipes, `Biobuf`s, child pids, and wait status.

Integration and risks:
- Shared by common tools, filterkit commands, and upas/fs support code.
- `Timefmt` is shared with folder append date handling.
