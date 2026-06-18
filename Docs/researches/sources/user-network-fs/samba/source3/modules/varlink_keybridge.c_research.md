<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.c -->
# sources/user-network-fs/samba/source3/modules/varlink_keybridge.c

## Purpose
This file implements a small client for Samba's container keybridge varlink protocol. It fetches configuration data, especially key material for encrypted CephFS shares, from a local varlink service so Samba does not need to know the service's remote-secret backend.

## Important APIs, Types, And Functions
The exported API is `varlink_keybridge_entry_get`. Internal helpers include `vlkb_kind_string`, `vlkb_error`, the varlink method callback `vlkb_get`, `vlkb_wait_for_response`, and `vlkb_entry_get`. The protocol uses method `org.samba.containers.keybridge.Get` and fields `name`, `scope`, `kind`, `entry`, `data`, with kind strings `B64` and `VALUE`.

## Control Flow
`varlink_keybridge_entry_get` delegates to `vlkb_entry_get`. That function builds a varlink object with requested name/scope/kind, opens a connection to `kbc->path`, allocates a talloc result, calls the `Get` method, then waits up to five seconds with `select` before processing events. The callback handles either a varlink error object or a successful `entry` object, extracts `kind` and `data`, fills `struct varlink_keybridge_result`, and closes the connection.

## State And Persistence
No durable state is stored. The only state is the transient varlink connection, request object, and talloc-owned result. Returned secret/config data is kept in `result->data` under the caller's memory context.

## Dependencies And Integration Points
The implementation depends on libvarlink, Samba debug/talloc infrastructure, and the public declarations in `varlink_keybridge.h`. It integrates share setup or filesystem-module code with a local secret provider over a Unix-socket-style varlink path.

## Risks
The five-second blocking `select` timeout is simple but can stall setup paths. On early setup failures before result allocation, `*resp` may remain untouched while the function returns false. Unknown kind strings default to `VALUE` behavior except explicit `B64`. Error responses include serialized JSON in the returned data string, which is useful diagnostically but may expose service-provided details in logs or callers.

## Test Signals
Useful tests include successful VALUE and B64 responses, server-side varlink errors, missing or malformed `entry`, `kind`, or `data` fields, connection failure, timeout, and talloc allocation failure handling. Integration tests need a local keybridge varlink service or mock.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.c -->
