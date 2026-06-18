# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/clnt_vc.c

Read completely: 794 lines.

This file implements connection-oriented/virtual-circuit RPC clients over record-marked streams: `clnt_vc_create` and VC client ops.

Key behavior: creation allocates `CLIENT` and `ct_data`, initializes per-fd lock arrays, connects the fd if needed, saves the remote address, pre-serializes the call header, creates an `xdrrec` stream using `read_vc`/`write_vc`, and defaults to AUTH_NONE. Calls lock by fd, update XID, marshal proc/auth/args, end the record immediately unless batching is requested, wait for matching-XID replies, decode reply headers/results, validate auth, and refresh credentials on auth errors. Control supports fd close policy, timeout, server address retrieval, fd retrieval, XID/program/version get/set. `read_vc` polls with the configured timeout; `write_vc` writes until all bytes are sent.

Important interactions: selected by `clnt_tli_create` for ordered connection transports and used for TCP-style RPC. Shares lock infrastructure and signal masking conventions with datagram clients.

Security/reliability notes: per-fd locking serializes shared descriptor use. The inline host/network order helpers assume aligned 32-bit access. Batched calls intentionally return before reading a response, so callers must only batch procedures that produce no replies.
