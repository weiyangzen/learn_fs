# File Research: sources/windows/dokany/sys/flush.c

Implements `IRP_MJ_FLUSH_BUFFERS` dispatch and completion.

Key entry points:
- `DokanDispatchFlush()` validates the file object/CCB, builds a `FLUSH_CONTEXT` with the target filename, uninitializes the cache map, performs an oplock check, and registers the IRP for user mode.
- `DokanCompleteFlush()` updates the CCB user context and completes with the status returned by user mode.

Core mechanics:
- Invalid or missing file context is treated as success, matching flush permissiveness for some close/volume edge cases.
- The FCB is locked read-only while the event context is built.
- `CcUninitializeCacheMap()` is called before the flush is forwarded to user mode.
- Oplock checks can post the IRP pending before normal Dokan registration.

Filesystem relevance:
- Flush connects Windows flush semantics to the user-mode filesystem and cache manager state.

Notable risks:
- Flush completion trusts user-mode status and does not itself force data persistence.
- The FCB unlock in `finally` assumes `fcb` was set only after locking; current flow satisfies that.
