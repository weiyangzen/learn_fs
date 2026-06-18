# sources/user-network-fs/libfuse/lib/fuse_uring_i.h

Purpose: `fuse_uring_i.h` is the internal interface between low-level session code and the optional io_uring transport implementation.

Important APIs, types, and functions: It defines default session options `SESSION_DEF_URING_ENABLE` and `SESSION_DEF_URING_Q_DEPTH`, declares `fuse_session_process_uring_cqe`, and, when `HAVE_URING` is true, declares `fuse_uring_start`, `fuse_uring_wake_ring_threads`, `fuse_uring_stop`, `send_reply_uring`, `fuse_reply_data_uring`, and `fuse_send_msg_uring`. Without `HAVE_URING`, it provides inline stubs returning `-ENOTSUP` or doing nothing.

Control flow: Compile-time conditionals select real prototypes or no-op stubs. This lets `fuse_lowlevel.c` call io_uring hooks without wrapping every call site in preprocessor conditionals.

State and persistence behavior: The header owns no state. Defaults influence initial `se->uring` values during session creation.

Dependencies and integration points: It includes `fuse_config.h`, `fuse_lowlevel.h`, and `fuse_kernel.h`, plus `util.h` for `FUSE_VAR_UNUSED` in non-uring builds. The real implementation is `fuse_uring.c`, and the main caller is `fuse_lowlevel.c` during INIT negotiation, reply sending, and CQE dispatch.

Risks: Header/implementation signature drift would break optional builds. Returning `-ENOTSUP` in stubs must be tolerated by callers. Defaults currently disable io_uring unless environment or options enable it, so tests must verify both paths.

Test signals: Build matrix coverage with `HAVE_URING=true` and false is essential. Runtime tests should assert no-uring builds link and report unsupported behavior cleanly while uring builds wire the real functions.
