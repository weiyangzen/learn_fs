# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/cache.c

No-op cache shim for drawterm’s kernel facade.

Key responsibilities:
- Defines empty `cinit`, `copen`, `cupdate`, and `cwrite`.
- Defines `cread()` returning zero.

Role in this group:
- Satisfies kernel cache API references without implementing a local cache.

Notable risks:
- Any caller expecting real cache persistence or read-back behavior receives no data.
