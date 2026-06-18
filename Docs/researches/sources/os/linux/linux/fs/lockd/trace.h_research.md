# File Research: sources/os/linux/linux/fs/lockd/trace.h

## Purpose
`trace.h` declares lockd trace events for NLM client lock operations. It defines symbolic NLM status formatting and a reusable trace event class for lock/test/unlock/grant operations.

## Main Responsibilities
- Sets `TRACE_SYSTEM lockd`.
- Defines `NLM_STATUS_LIST` differently depending on whether NLMv4 support is enabled.
- Registers NLM status enum values for trace decoding.
- Provides `show_nlm_status()` symbolic formatting.
- Declares the `nlmclnt_lock_event` event class capturing owner hash, svid, file handle hash, range, remote address, and status.
- Defines concrete events: `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, and `nlmclnt_grant`.

## Key Fields
- `oh`: CRC32-derived owner-handle hash, avoiding dumping full owner bytes.
- `svid`: NLM server/client supplied owner PID.
- `fh`: hashed NFS file handle.
- `start` and `len`: requested lock range stored from `nlm_lock`.
- `addr`: socket address copied through tracepoint sockaddr helpers.
- `status`: protocol status converted from big-endian to CPU order.

## Integration Points
- Included by `trace.c` with `CREATE_TRACE_POINTS` for instantiation.
- Included from lockd paths that emit these trace events.
- Uses generic tracepoint headers, CRC32, NFS file handle hashing, and lockd structures.

## Risks and Edge Cases
- Status symbol coverage depends on `CONFIG_LOCKD_V4`; non-v4 builds expose only the smaller status list.
- Trace output intentionally hashes file handles and owner handles instead of exposing complete opaque values.
