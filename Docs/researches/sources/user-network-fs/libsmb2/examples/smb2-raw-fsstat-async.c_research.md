# sources/user-network-fs/libsmb2/examples/smb2-raw-fsstat-async.c

Purpose: This raw async example sends a compound CREATE/QUERY_INFO/CLOSE sequence to retrieve filesystem information at a selectable info level.

Important APIs and types: It uses `smb2_create_request`, `smb2_query_info_request`, `smb2_close_request`, `smb2_cmd_create_async`, `smb2_cmd_query_info_async`, `smb2_cmd_close_async`, `smb2_add_compound_pdu`, `compound_file_id`, filesystem info structs, `nterror_to_errno`, and a poll-driven wait helper.

Control flow: The program parses the info level, connects to the share, allocates `stat_cb_data`, builds a compound request where query and close refer to the compound file id, queues it, waits for callback completion, prints fields based on the selected filesystem info class, frees decoded data, and disconnects.

State and persistence behavior: It does not mutate remote state except transient open/close. Runtime state is callback status, decoded query output, and compound status accumulation.

Dependencies and integration points: It tests libsmb2's raw command builders, compound request chaining, filesystem info decoders, and sync-style wait loop over async commands.

Risks: Unsupported info levels can leave output handling ambiguous. The final `fs = cb_data.ptr` is freed even though the generic callback receives `0` from `stat_cb_3`, so freeing `NULL` is expected for this code path. Error paths can leak already allocated PDUs or context state.

Test signals: Run against known shares for volume, size, device, control, and full-size info levels and verify printed values match server properties. Compound status errors should surface as nonzero callback status.
