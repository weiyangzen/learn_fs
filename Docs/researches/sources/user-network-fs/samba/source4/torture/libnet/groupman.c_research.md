# sources/user-network-fs/samba/source4/torture/libnet/groupman.c

## Purpose

`groupman.c` tests the libnet RPC group-add convenience function against SAMR and verifies cleanup through shared helpers.

## Important APIs, Types, and Functions

- `test_groupadd()` calls `libnet_rpc_groupadd()` with a domain handle and group name.
- `torture_groupadd()` connects to SAMR, opens the domain, adds `TEST_GROUPNAME`, and cleans it up.
- `TEST_GROUPNAME` comes from `grouptest.h` as `libnetgrptest`.

## Control Flow

The test opens a SAMR RPC connection, opens the configured workgroup domain through shared helper code, calls the libnet group-add wrapper, and deletes the group with `test_group_cleanup()` before freeing the memory context.

## State and Persistence Behavior

It creates and deletes one SAMR group. A failure after creation but before cleanup can leave `libnetgrptest` in the directory.

## Dependencies and Integration Points

Dependencies include SAMR RPC bindings, `libnet_rpc_groupadd()`, shared domain/group helper prototypes, loadparm workgroup, and the `net.groupadd` suite registration in `libnet.c`.

## Risks and Edge Cases

Name collisions with existing `libnetgrptest` groups can fail creation or cleanup. The test only verifies the add call succeeds, not group attributes beyond existence. Cleanup must be reliable to avoid persistent test artifacts.

## Test Signals

Passing signals are successful RPC connection, domain open, `libnet_rpc_groupadd()` status, and group cleanup.
