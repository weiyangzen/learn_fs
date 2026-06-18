<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.h -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.h

## Purpose

This header declares the small I/O structures shared by outbound WREPL helper APIs.

## Important APIs, Types, and Functions

- `struct wreplsrv_pull_cycle_io` carries a partner, optional owner table, and optional existing outbound connection for a pull cycle.
- `struct wreplsrv_push_notify_io` carries a partner plus flags selecting inform/update and propagation behavior.

## Control Flow

The header contains no functions. Callers populate these structures and pass them to helper functions declared elsewhere/generated from `wrepl_out_helpers.c`.

## State and Persistence Behavior

The structures reference partner, owner arrays, and optional connection state owned by callers or talloc parents. They do not persist state themselves.

## Dependencies and Integration Points

It is included by WREPL outbound/inbound scheduler code that starts pull cycles and push notifications.

## Risks and Edge Cases

Ownership of `owners` and `wreplconn` is transferred or stolen in helper implementations, so callers must follow the expected talloc lifetime rules.

## Test Signals

Correct compilation and successful async pull/push flows validate the structure contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_helpers.h -->
