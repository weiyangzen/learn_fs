# sources/user-network-fs/libsmb2/examples/smb2-CMD-FIND.c

Purpose: This example is a protocol probe for SMB2 `QUERY_DIRECTORY` behavior, especially `SMB2_RESTART_SCANS` and `SMB2_INDEX_SPECIFIED`.

Important APIs and types: It uses raw libsmb2 types `smb2_create_request`, `smb2_query_directory_request`, `smb2_query_directory_reply`, `smb2_fileidfulldirectoryinformation`, `smb2_pdu`, file IDs, `smb2_cmd_create_async`, `smb2_cmd_query_directory_async`, `smb2_queue_pdu`, `smb2_decode_fileidfulldirectoryinformation`, fd event callbacks, and `poll`.

Control flow: The program initializes an SMB2 context, registers fd/event callbacks, parses a URL, connects asynchronously, opens the share root, scans directory entries, stores the first two names and indexes, restarts the scan from the beginning, then attempts to restart at the second index. The main loop polls the callback-provided fd/events and calls `smb2_service`.

State and persistence behavior: Runtime state is held in global `is_finished`, callback fd/event globals, and `struct app_data` containing file ID, two indexes, and duplicated names. There is no persistent state.

Dependencies and integration points: It exercises low-level create/query-directory commands rather than the higher-level `smb2_opendir` wrapper, and it is useful for testing server conformance around directory index semantics.

Risks: `is_finished` is never set on the successful path, so the program can continue polling indefinitely unless a later service error occurs. `qd_2_cb` appears to queue the index-specified request with `qd_2_cb` again rather than `qd_3_cb`, so the intended third-stage validation may not run. Duplicated names are never freed.

Test signals: Expected output includes first and second entries, restart returning the first entry, and index-specified restart returning the second entry. A hanging process or repeated second-stage callback indicates the control-flow risks above.
