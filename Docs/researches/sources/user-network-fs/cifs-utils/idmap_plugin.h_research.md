<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.h -->
# sources/user-network-fs/cifs-utils/idmap_plugin.h

## Purpose

`idmap_plugin.h` declares the helper-facing ID mapping plugin wrapper API.

## Important APIs, Types, and Functions

It exposes `plugin_errmsg`, `init_plugin`, `exit_plugin`, `sid_to_str`, `str_to_sid`, `sids_to_ids`, and `ids_to_sids`, all operating on types from `cifsidmap.h`.

## Control Flow

Programs initialize a plugin handle once, call conversion helpers as needed, inspect `plugin_errmsg` on failure, and call `exit_plugin`.

## State and Persistence Behavior

Plugin state is opaque and handle-based. Error message state is global and not caller-owned.

## Dependencies and Integration Points

It includes `cifsidmap.h` and is consumed by idmap and ACL utilities.

## Risks and Edge Cases

The API does not carry an error buffer per handle, so concurrent or nested calls could overwrite `plugin_errmsg`. Callers must free names returned by `sid_to_str`.

## Test Signals

Compile and fake-plugin tests should verify caller ownership, missing symbol handling, and consistent error strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.h -->
