# File Research: sources/os/plan9/9front/sys/src/9/cycv/init9.s

Tiny Cyclone V user-init assembly stub.

Key responsibilities:
- Defines `_main`.
- Calls `main`.
- Calls `exits` if `main` returns.

Role:
- Minimal user/runtime entry glue for this architecture.
