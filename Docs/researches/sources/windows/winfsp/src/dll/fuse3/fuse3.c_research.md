# File Research: sources/windows/winfsp/src/dll/fuse3/fuse3.c

This file exposes higher-level FUSE3 entry points.

Key responsibilities:
- `fsp_fuse3_main_real` mirrors the FUSE2 main flow: parse command line, create FUSE3 object, mount it through the adapter, daemonize, install signal handlers, run loop, then unmount/destroy.
- `fsp_fuse3_lib_help` triggers core option help handling.
- Loop APIs delegate to FUSE2 loop functions:
  - `fsp_fuse3_loop`
  - `fsp_fuse3_loop_mt_31`
  - `fsp_fuse3_loop_mt`
- `fsp_fuse3_exit` delegates to `fsp_fuse_exit`.
- `fsp_fuse3_get_context` aliases the FUSE2 context after static layout checks.
- Connection-info option parsing/apply functions are stub-compatible.
- Version helpers return configured FUSE version/package version.

Filesystem relevance:
- This is the public FUSE3 lifecycle facade.
- Its loop and context APIs prove that FUSE3 execution shares the same runtime state as the FUSE2 adapter.
