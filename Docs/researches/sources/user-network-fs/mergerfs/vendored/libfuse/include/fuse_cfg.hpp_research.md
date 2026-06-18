<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_cfg.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_cfg.hpp

Purpose: `fuse_cfg_t` stores process-wide configuration for the vendored FUSE runtime, including identity overrides, debug logging, kernel negotiation limits, passthrough depth, thread counts, queue depth, CPU pinning policy, and request timeout.

Important APIs and state: `valid_uid`, `valid_gid`, and `valid_umask` validate sentinel-backed settings. `log_file()` and `log_filepath()` getters/setters protect shared log sink state with a `std::shared_mutex`; the default log file is a non-owning `stderr` shared pointer. The header declares global `fuse_cfg`.

Control flow and integration: command-line/config parsing populates this global, debug tracing reads it, and session/init negotiation consumes max background, max pages, passthrough stack depth, thread counts, pinning, and timeouts.

Risks and test signals: global mutable state affects all mounts in-process, and FILE ownership is controlled by custom shared-pointer deleters in debug code. Tests should cover concurrent log sink replacement, defaults, valid/invalid sentinel handling, and config propagation into init replies and thread-pool setup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_cfg.hpp -->
