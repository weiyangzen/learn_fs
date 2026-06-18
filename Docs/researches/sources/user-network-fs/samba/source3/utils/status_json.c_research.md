# sources/user-network-fs/samba/source3/utils/status_json.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_json.c` implements JSON emitters for `smbstatus`. It converts sessions, tree connections, open files, byte-range locks, notify records, profile counters, server IDs, access masks, share modes, oplocks, leases, crypto state, and timestamps into the `state->root_json` object. The source was read as a complete 1446-line file.

## Important APIs, Types, and Functions

Public functions are `add_general_information_to_json`, `add_section_to_json`, `add_profile_item_to_json`, `add_profile_persvc_item_to_json`, `traverse_connections_json`, `traverse_sessionid_json`, `print_share_mode_json`, `print_brl_json`, and `print_notify_rec_json`. Important helpers include `add_server_id_to_json`, `map_mask_to_json`, `add_nested_item_to_json`, `add_crypto_to_json`, channel emitters, access/caching/oplock/lease/sharemode emitters, `lease_key_to_str`, `add_open_to_json`, `add_fileid_to_json`, and `add_lock_to_json`.

## Control Flow

`smbstatus` creates `root_json`, calls `add_general_information_to_json`, adds empty sections before each traversal, and each callback updates the relevant section object. Sessions are keyed by session id and include channels. Tcons are keyed by tree-connect id. Open files are keyed by service path plus filename and contain nested `opens` keyed by server id/share file id. Byte-range locks are keyed by share path plus filename and contain a `locks` array. Notify records are keyed by server id.

## State and Persistence Behavior

The file only mutates the in-memory JSON tree. It uses talloc stack frames for temporary strings and frees temporary JSON objects on failure. It reads fields supplied by `status.c`, including live session globals, connection data, share-mode entries, lease state, and notify instances.

## Dependencies and Integration Points

It depends on Jansson through Samba's `audit_logging` JSON wrappers, `smbprofile`, `conn_tdb`, `session`, generated NDR structs, security/open-file constants, server ID utilities, time conversion, and `status.h`. It is selected in `wscript_build` only when `HAVE_JANSSON` is configured.

## Risks and Edge Cases

`map_mask_to_json` asserts that all bits are known, so new access/oplock/share/lease bits can crash debug/assert builds until the tables are updated. Several section updates rely on `json_get_object` behavior for missing keys after `add_section_to_json`; calling emitters without preparation can fail. Path-based JSON keys can collide for repeated names or unusual path normalization. The JSON object update pattern is verbose and error-prone if future helpers forget to free invalid objects.

## Test Signals

Tests should compare JSON schema for sessions, tcons, opens, locks, notify records, profile sections, UID resolution on/off, lease and oplock combinations, unknown/expanded mask bits, no data sections, and builds with and without Jansson.
