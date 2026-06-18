# File Research: sources/windows/winfsp/src/dll/fuse/fuse_compat.c

Export shim for traditional `fuse_*` symbols.

Key responsibilities:
- Documents that normal C/C++ users should consume `fsp_fuse_*` symbols via headers/macros.
- Defines `FSP_FUSE_API` empty and `FSP_FUSE_SYM` as a `__declspec(dllexport)` wrapper.
- Includes `fuse_common.h`, `fuse.h`, and `fuse_opt.h` to instantiate exported `fuse_*` forwarding symbols.
- Uses the default `fsp_fuse_env`.

Dependencies:
- Includes `dll/library.h` and public FUSE compatibility headers.

Filesystem relevance:
- Supports FFI consumers that look up conventional FUSE symbol names directly, such as Python or JVM FUSE bindings.

Notable risks:
- This is intentionally a compatibility/export layer; new native users should avoid depending on these direct symbols when the `fsp_fuse_*` API is available.
