# File Research: sources/os/plan9/9front/sys/src/cmd/mk/file.c

Wraps file/archive time lookup, touch/delete operations, and `-w` what-if timestamp initialization.

Key behavior:
- `timeof()` consults archive handling for names containing `(`, otherwise uses cached `S_TIME` entries unless forced.
- `touch()` updates files or archive members, respecting `nflag`.
- `delete()` removes regular files but refuses archive member deletion.
- `timeinit()` marks comma/space/newline-separated names as having the current time.

Important dependencies: `mk.h`, `mkmtime`, `atimeof`, `atouch`, `chgtime`, `S_TIME`.

Notable risks:
- Any name containing `(` is treated as archive syntax.
- `delete()` cannot remove archive members, so failed recipe cleanup is incomplete for such targets.
