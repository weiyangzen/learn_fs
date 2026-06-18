# sources/user-network-fs/samba/source3/libsmb/clierror.c

## Purpose

`clierror.c` provides two small client utility functions: mapping SMB/NT status values to local `errno` values and checking whether a `cli_state` is initialized and connected.

## Important APIs and Functions

- `cli_status_to_errno(NTSTATUS status)` converts DOS-class statuses to NTSTATUS first, special-cases `NT_STATUS_STOPPED_ON_SYMLINK` to `EACCES`, then calls `map_errno_from_nt_status()`.
- `cli_state_is_connected(struct cli_state *cli)` returns false for `NULL` or uninitialized clients and otherwise delegates to `smbXcli_conn_is_connected(cli->conn)`.

## Control Flow

`cli_status_to_errno()` starts by detecting DOS-encoded NTSTATUS values with `NT_STATUS_IS_DOS()`, extracting DOS class/code, and translating through `dos_to_ntstatus()`. It preserves legacy Samba behavior for stopped-on-symlink because the status value shape would not map correctly through the generic mapper. It logs the numeric NTSTATUS and resulting errno at notice level before returning.

`cli_state_is_connected()` is a defensive guard: it checks pointer validity, `cli->initialised`, and then the underlying connection state.

## State and Persistence Behavior

No persistent state is modified. The only side effect is logging from `cli_status_to_errno()`.

## Dependencies and Integration Points

This file depends on `source3/include/client.h`, source3 libsmb prototypes, NTSTATUS/DOS status helpers, `map_errno_from_nt_status()`, and `smbXcli_conn_is_connected()`. It is used by callers that need POSIX-style errors or cheap connection liveness checks without knowing `cli_state` internals.

## Risks and Edge Cases

- Error mapping is lossy by nature; callers must retain NTSTATUS where exact protocol diagnostics matter.
- The stopped-on-symlink special case preserves legacy behavior and should not be removed without checking symlink traversal callers.
- `cli_state_is_connected()` assumes initialized clients have a valid `conn` pointer; malformed partially constructed states are not fully protected.

## Test Signals

Tests should include DOS-class status conversion, symlink-stop mapping to `EACCES`, representative NTSTATUS-to-errno mappings, null and uninitialized `cli_state` checks, connected/disconnected underlying `smbXcli_conn` states, and log output stability where diagnostics are asserted.
