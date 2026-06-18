## sources/user-network-fs/nfs-utils/utils/statd/system.h

Purpose: Compatibility definitions for fd-set types used by statd service-loop code.

Important APIs/types/functions: Defines `FD_SET_TYPE` and `SVC_FDSET` as either `fd_set`/`svc_fdset` or legacy `int`/`svc_fds`.

Control flow: Preprocessor-only compatibility layer.

State and persistence: No state.

Dependencies and integration: Included by `statd.h`; shields users from SunRPC implementation differences.

Risks and test signals: Build portability depends on correct branch selection. Compile tests should cover modern and legacy RPC headers if supported.
