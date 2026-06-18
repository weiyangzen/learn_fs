## sources/user-network-fs/libtirpc/src/clnt_dg.c

Purpose: Implements the connectionless datagram RPC `CLIENT` transport used for UDP-style netconfig entries.

Important APIs and control flow: `clnt_dg_create` creates a `CLIENT`, allocates one private `cu_data` block containing input/output buffers, pre-marshals the static call header, enables nonblocking I/O, optionally enables Linux `IP_RECVERR`, and attaches per-fd locking from `clnt_fd_locks.h`. `clnt_dg_call` serializes procedure/auth/arguments, increments XID, sends with `sendto` or a connected socket, polls for replies, retransmits on retry timeout until total timeout, filters replies by XID unless async mode is enabled, decodes reply status, validates/unpacks auth, and refreshes credentials up to two times except for RPCSEC_GSS.

State and persistence: Per-client state tracks fd, remote address, retry/total timeouts, async/connect flags, cached error, and pre-marshalled XDR position. Global `dg_fd_locks` serializes all handles sharing a file descriptor.

Dependencies and integration: Used by `clnt_tli_create` for `NC_TPI_CLTS`. Depends on `authnone_create`, XDR, poll, socket APIs, `clnt_fd_lock`, and optional GSS.

Risks and test signals: The fd lock is held across full RPC/retransmission. Tests should cover timeout math, XID mismatch filtering, async mode, `CLSET_*` controls, IP error queue handling, destroy while operations are pending, and shared-fd serialization.
