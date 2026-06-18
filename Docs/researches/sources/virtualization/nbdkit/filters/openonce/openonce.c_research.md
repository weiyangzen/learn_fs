# File Research: sources/virtualization/nbdkit/filters/openonce/openonce.c

This filter opens the underlying plugin once per `(readonly, is_tls, exportname)` tuple, then reuses the same `nbdkit_next` context across multiple client connections. A global vector of `export_entry` records is protected by `export_list_lock`.

`.open` searches for an existing matching context; if absent, it duplicates the export name, calls `nbdkit_next_context_open(..., shared=1)`, prepares the new context, and appends it to the global list. Per-client handles only store the selected shared `next` pointer. `.cleanup` finalizes and closes all retained contexts at server shutdown, noting that finalize failure could imply data loss.

Because requests from different clients can now hit a shared backend context, `.thread_model` upgrades `SERIALIZE_REQUESTS` to `SERIALIZE_ALL_REQUESTS`. All capability, metadata, I/O, extent, and cache callbacks delegate to the handle's stored `h->next` rather than the callback's `next` argument.

The key tradeoff is connection lifetime: contexts remain open even after the last client disconnects. The code comments identify possible future close-on-unused behavior, but the current design favors persistent backend state over resource reclamation.
