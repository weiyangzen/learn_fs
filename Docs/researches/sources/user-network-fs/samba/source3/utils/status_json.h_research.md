# sources/user-network-fs/samba/source3/utils/status_json.h

## Purpose

`sources/user-network-fs/samba/source3/utils/status_json.h` declares the JSON output interface used by `smbstatus` and profile dumping. The source was read as a complete 84-line file.

## Important APIs, Types, and Functions

It declares section/general/profile helpers plus traversal emitters for connections, sessions, share modes, byte-range locks, and notify records. Parameters expose the data contracts from `conn_tdb`, `sessionid`, `share_mode_data`, `share_mode_entry`, `file_id`, `server_id`, `notify_instance`, `brl_flavour`, and `enum crypto_degree`.

## Control Flow

The header has no executable flow. `status.c` calls `add_section_to_json` before traversals and calls the typed JSON functions from callbacks. `status_profile.c` calls profile item helpers when `state->json_output` is true.

## State and Persistence Behavior

All functions mutate the in-memory `struct traverse_state` root JSON object and do not own persistent storage.

## Dependencies and Integration Points

It includes `status.h` and notifyd DB declarations. The implementations are either the real Jansson-backed `status_json.c` or no-op fallbacks in `status_json_dummy.c`, selected by the build.

## Risks and Edge Cases

The header is compiled even for non-Jansson builds, so declarations must remain compatible with dummy implementations. Any signature change must be synchronized with `status.c`, `status_profile.c`, `status_json.c`, and `status_json_dummy.c`.

## Test Signals

Compile coverage for both implementation variants and integration tests for `smbstatus --json` are the primary signals.
