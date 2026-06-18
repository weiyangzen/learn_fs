# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/dat.h

This small header defines a linked-list address type for filterkit commands.

Key contents:
- `Addr` contains `next` and string `val`.
- Declares `readaddrs(char*, Addr*)`, which appends parsed addresses from a file.

Integration and risks:
- Shared by `deliver`, `list`, `mbappend`, `mbcreate`, `mbremove`, `readaddrs`, and `token`.
