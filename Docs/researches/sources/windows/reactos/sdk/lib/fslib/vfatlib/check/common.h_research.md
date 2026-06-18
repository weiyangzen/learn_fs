# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.h

This header declares shared checker utilities and maps them for ReactOS.

Core contents:
- Declares or macro-wraps `die` and `pdie`.
- Under ReactOS, maps `die(...)` and `pdie(...)` to debug strings with file/line context.
- Declares ReactOS heap wrappers `vfalloc`, `vfcalloc`, and `vffree`; non-ReactOS declares `alloc`.
- Declares queued allocation helpers `qalloc`/`qfree`, `min`, and `get_key`.

Risk points:
- `die` and `pdie` are macros in ReactOS, so call-site semantics differ from normal functions.
- Header assumes several surrounding definitions such as `__RELFILE__`, `DECLSPEC_NORETURN`, and checker global conventions.
