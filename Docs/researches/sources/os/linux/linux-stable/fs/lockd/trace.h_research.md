# File Research: sources/os/linux/linux-stable/fs/lockd/trace.h

## Summary
Trace event definitions for lockd client-side lock operations.

## Main APIs
Defines status enums and the event class `nlmclnt_lock_event`, then instantiates `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, and `nlmclnt_grant`.

## Behavior
Trace records include sockaddr, owner-handle CRC, server process id, NFS file-handle hash, lock start/length, and symbolic NLM status. Status symbol sets differ when `CONFIG_LOCKD_V4` is enabled.

## Dependencies
Linux tracepoint framework, CRC32, NFS file-handle hashing, and lockd structures.

## Risks
Trace output deliberately hashes handles rather than dumping opaque data. Status decoding must stay aligned with NLM status constants and v4 configuration.
