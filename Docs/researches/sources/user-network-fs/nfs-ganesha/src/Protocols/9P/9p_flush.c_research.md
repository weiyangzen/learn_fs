## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_flush.c

Purpose: implements `TFLUSH`, coordinating cancellation ordering for earlier 9P requests on the same connection.

APIs and flow: `_9p_flush` parses tag and oldtag, calls `_9p_FlushFlushHook` with the connection and current request sequence, and always returns `RFLUSH` after the hook has synchronized with the target request if found.

State/dependencies: it depends on the flush hook subsystem in `9p_flush_hook.c`, especially per-connection flush buckets and request sequence numbers. It does not touch FSAL or fid state directly.

Risks/tests: correctness depends on not replying before an older matching request has finished. Test flush for missing oldtag, active oldtag, newer same tag, and concurrent request completion.
