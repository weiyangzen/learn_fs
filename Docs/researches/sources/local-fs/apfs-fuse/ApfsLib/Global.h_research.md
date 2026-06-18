# File Research: sources/local-fs/apfs-fuse/ApfsLib/Global.h

This small header declares process-wide debug and lax-mode globals used by the APFS library. `g_debug` and `g_lax` are defined elsewhere, with comments pointing to `ApfsContainer.cpp`.

It also defines debug flag bits through `DbgFlags`: errors, informational logging, directory tracing, compressed-file tracing, and crypto tracing. Utility logging functions and crypto/keybag dump paths use these flags to decide what to print.

The file has no implementation logic and exists as a shared declaration point. Because it exposes mutable globals, behavior such as logging verbosity and lax validation is configured process-wide rather than per-container or per-mount.
