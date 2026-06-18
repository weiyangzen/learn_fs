# sources/user-network-fs/samba/source4/torture/rpc/mdssvc.c

## Purpose

This file is the RPC torture suite for Samba's `mdssvc` Spotlight metadata service. It validates basic open/close behavior, disabled or unknown Spotlight shares, invalid policy-handle handling, malformed and crafted metadata command blobs, marshalling type safety, and the server response for fetching attributes of an unknown CNID.

## Important APIs, Types, and Functions

The key state carrier is `struct torture_mdsscv_state`, which stores the RPC pipe, mdssvc policy handle, device ID, flags, and command-specific fields used across `open`, `unknown1`, `cmd`, and `close` calls. The main fixture helpers are `torture_rpc_mdssvc_setup()`, `torture_rpc_mdssvc_teardown()`, `torture_rpc_mdssvc_open()`, and `torture_rpc_mdssvc_close()`.

Important test functions are `test_mdssvc_open_unknown_share()`, `test_mdssvc_open_spotlight_disabled()`, `test_mdssvc_close()`, `test_mdssvc_null_ph()`, `test_mdssvc_invalid_ph_unknown1()`, `test_mdssvc_invalid_ph_cmd()`, `test_mdssvc_invalid_ph_close()`, `test_mdssvc_sl_unpack_loop()`, `test_sl_dict_type_safety()`, and `test_mdssvc_fetch_attr_unknown_cnid()`. The file uses generated `dcerpc_mdssvc_*` client stubs plus mdssvc `dalloc` and Spotlight marshalling helpers (`sl_pack_alloc()`, `sl_unpack()`, `dalloc_add*()`, `dalloc_get()`, and `dalloc_dump()`).

## Control Flow

The suite is fixture-driven. Simple `rpccmd` tests connect to mdssvc and issue isolated open/close or bad-handle calls. The `disconnect1`, `disconnect2`, and `disconnect3` test cases use `torture_rpc_mdssvc_open()` to open an mdssvc session first, then deliberately submit invalid handles to `unknown1`, `cmd`, or `close`; these expect `NT_STATUS_RPC_PROTOCOL_ERROR` and free the pipe because the connection is no longer usable.

`torture_rpc_mdssvc_open()` reads torture settings `spotlight_share` and `share_mount_path`, opens the service with `dcerpc_mdssvc_open()`, then calls `dcerpc_mdssvc_unknown1()` to initialize status and flags. `torture_rpc_mdssvc_close()` closes the stored handle if the pipe is still live.

The command tests construct Spotlight request blobs. `test_mdssvc_sl_unpack_loop()` sends a static byte buffer that represents a previously problematic unpacking pattern. `test_sl_dict_type_safety()` builds nested arrays and dictionaries with contexts and query parameters, packs them into a blob, and sends `mdssvc_cmd`. `test_mdssvc_fetch_attr_unknown_cnid()` builds a `fetchAttributes:forOIDArray:context:` request for a large unknown inode/CNID, unpacks the response, and asserts the returned path object is `sl_nil_t`.

## State and Persistence Behavior

The tests open server-side mdssvc handles and close them through fixture teardown. They use random device IDs and temporary client-side dalloc trees. They do not intentionally persist metadata or server configuration, but they require server-side Spotlight share configuration. Invalid policy-handle tests intentionally break the RPC pipe; teardown copes with this by treating a NULL pipe as already disconnected.

## Dependencies and Integration Points

The file integrates the generated mdssvc RPC client, Samba torture RPC connection helpers, runtime settings from `torture_setting_string()`, POSIX UID/GID for `unknown1`, random ID generation, and the internal mdssvc marshalling/dalloc implementation. It assumes named mdssvc shares exist according to settings: `spotlight_share` defaults to `spotlight`, `no_spotlight_share` defaults to `no_spotlight`, `unknown_share` defaults to `choukawoohoo`, and `share_mount_path` defaults to `/foo/bar`.

## Risks and Edge Cases

This suite is sensitive to server configuration. Share names and Spotlight enablement must match expectations or open tests will fail. The invalid-handle tests require the server to terminate or poison the RPC context consistently with `NT_STATUS_RPC_PROTOCOL_ERROR`; subsequent use of the same pipe is unsafe. The static unpack-loop buffer and crafted dalloc structures are regression/fuzz-style inputs, so changes in marshalling may surface memory-safety or compatibility issues. There are a few assertion-goto calls that pass `ret` where `ok` is the local boolean, so edits should preserve current semantics carefully.

## Test Signals

Important signals include unchanged input IDs for unknown/disabled shares, empty `share_path`, all-zero policy handles for failed opens or NULL handles, close returning the same policy-handle blob, protocol errors for random invalid handles, successful command submission for crafted Spotlight blobs, successful pack/unpack operations, and `sl_nil_t` as the path result for an unknown CNID. The exported `torture_rpc_mdssvc()` suite groups these signals into `rpccmd`, disconnect, and `mdscmd` test cases.
