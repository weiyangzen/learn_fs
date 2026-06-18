# File Research: sources/virtualization/spdk/lib/trace/trace.c

This file implements SPDK trace shared-memory initialization, trace event recording, per-core/per-user-thread trace histories, and cleanup.

`_spdk_trace_record()` is the hot path. It selects a per-lcore trace history from the current SPDK env core or from thread-local user-thread registration, fills the next circular trace entry, validates the runtime argument count against the registered tracepoint definition, copies integer/pointer/string arguments across one or more `spdk_trace_entry_buffer` slots, null-terminates truncated strings, issues a write memory barrier, and advances `history->next_entry`.

`spdk_trace_init()` builds the shared-memory file layout. It sizes sections for main metadata, owner records, tracepoint masks, owner types, object types, tracepoint definitions, lcore offsets, and all per-core/user-thread histories. It opens/truncates/mmaps the shm object, mlocks on Linux, zeroes the file, initializes section offsets and counts, assigns histories for each SPDK env core and configured user thread slot, then calls `trace_flags_init()` to register trace definitions and owner-id allocation.

User thread support is managed by `spdk_trace_register_user_thread()` and `spdk_trace_unregister_user_thread()`. They require callers not to be on a dedicated SPDK core, allocate a slot from `g_ut_array`, map it to the trace history index range after dedicated cores, store the pthread name, and keep the selected history in thread-local storage.

`spdk_trace_cleanup()` finalizes trace flags, decides whether to unlink the shm object only when no trace entries were recorded, unmaps/closes the trace file, frees the user-thread bit array, and leaves recorded trace files available for postmortem debugging.

Important invariants are the shared-memory section layout, power-of-two circular trace history indexing, matching tracepoint argument definitions, buffer-continuation entries using `SPDK_TRACE_MAX_TPOINT_ID`, and the memory barrier before advancing `next_entry`. The cleanup path unmaps only `sizeof(struct spdk_trace_file)` rather than the full mapped size as read, which is worth checking if changing trace-file lifetime behavior.
