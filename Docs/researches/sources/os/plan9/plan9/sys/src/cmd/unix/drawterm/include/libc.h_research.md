# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libc.h

Minimal compatibility header.

Key contents:
- Includes `lib.h`.

Role in this group:
- Lets source files written for Plan 9 `<libc.h>` include the drawterm portability definitions.

Notable risks:
- No include guard; repeated inclusion relies on the idempotence of included declarations/macros.
