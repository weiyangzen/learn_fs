# sources/user-network-fs/samba/source3/winbindd/winbindd_change_machine_acct.c

## Purpose

`winbindd_change_machine_acct.c` implements the async parent-side handler for `WINBINDD_CHANGE_MACHINE_ACCT`. It resolves the target domain and forwards machine-account password changes to the domain child over generated `wbint` DCERPC.

## Important APIs, Types, and Functions

- `struct winbindd_change_machine_acct_state` is an empty tevent state holder.
- `winbindd_change_machine_acct_send()` validates domain input and starts `dcerpc_wbint_ChangeMachineAccount_send()`.
- `winbindd_change_machine_acct_done()` merges transport status and remote result.
- `winbindd_change_machine_acct_recv()` returns `tevent_req_simple_recv_ntstatus()`.

## Control Flow

The send path creates a tevent request, optionally extracts a requested DC name, resolves `request->domain_name`, and fails with `NT_STATUS_NO_SUCH_DOMAIN` if needed. Internal domains complete immediately because they are passdb-based and the code explicitly avoids unsafe AD DC local password-change semantics. External domains are forwarded to `dom_child_handle(domain)`. The callback fails if either the RPC status or child result is not OK.

## State and Persistence Behavior

This file stores no durable state. Durable machine-account changes happen in child-side code and secrets/passdb layers. Local state is only the tevent request lifecycle.

## Dependencies and Integration Points

It integrates with winbind domain lookup, domain child handles, tevent, and generated `ndr_winbind_c.h` client stubs. It is part of winbind's async command dispatch path.

## Risks and Edge Cases

Internal domains are treated as success without rotating a password. Explicit DC affinity is passed only when present. Correct error propagation depends on checking both generated RPC status and child result.

## Test Signals

Test missing-domain failure, internal-domain short-circuit success, external-domain forwarding with and without a DC name, remote operation failure propagation, and transport failure propagation.
