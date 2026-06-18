# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/compat.h

## Role

`compat.h` declares the kernel-like compatibility API and data structures used by the VNC server's synthetic Plan 9 devices and 9P exporter.

## Main Definitions

- `Ref`, `Rendez`, `Chan`, `Cname`, `Dev`, `Dirtab`, `Walkqid`, and `Proc`.
- `Dev` function table matching Plan 9 device entry points: reset, init, attach, walk, stat, open, create, close, read, write, remove, and wstat.
- Channel flags such as `COPEN` and `CFREE`.
- Error stack constants and `waserror()`/`poperror()` macros.
- Externs for `up`, `eve`, `devtab`, device helpers, channel helpers, rendezvous helpers, exporter/mounter helpers, shutdown, and screen initialization.

## Notable Limitations And Risk Areas

- It exposes a compact subset of kernel structures, so code ported from kernel space may require adaptation if it expects fields not represented here.
- The `Rendez` name is remapped through a macro to avoid namespace collision.
- `waserror()` increments `nerrlab` before `setjmp`; balancing with `poperror()` is critical.
