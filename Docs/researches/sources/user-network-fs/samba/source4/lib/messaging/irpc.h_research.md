# sources/user-network-fs/samba/source4/lib/messaging/irpc.h

## Purpose

`irpc.h` defines Samba's internal RPC-over-messaging header contract. It lets services register NDR-backed server callbacks, create DCERPC binding handles, attach security tokens, and manage task names.

## Important APIs, Types, and Functions

The central type is `struct irpc_message`, carrying sender ID, private data, IRPC header, NDR pull context, reply flags, messaging context, registration pointer, and decoded data. `irpc_function_t` is the server callback signature. `IRPC_REGISTER()` wraps `irpc_register()`. Other declarations include binding-handle constructors, `irpc_binding_handle_add_security_token()`, name add/lookup/list/remove helpers, and `irpc_send_reply()`.

## Control Flow

There is no implementation flow in the header. Runtime flow is registration by service, lookup or binding by clients, messaging transport of NDR calls, callback execution, and reply send/defer/no-reply decisions.

## State and Persistence Behavior

State lives in messaging contexts and name records. `IRPC_CALL_TIMEOUT` defaults calls to 10 seconds, and `IRPC_CALL_TIMEOUT_INF` disables timeout. Per-message fields control reply lifecycle.

## Dependencies and Integration Points

It depends on Samba messaging, WERROR helpers, and generated IRPC NDR definitions. Services such as LDAP use IRPC name registration, and other internal tasks use these APIs for task-to-task RPC.

## Risks and Edge Cases

The callback request pointer is `void *`, so type safety depends on matching NDR table and call IDs. Deferred replies require careful message lifetime management. Name lookup can be affected by stale or missing server-id records.

## Test Signals

Coverage should include registration, name add/remove/lookup, binding by name and server ID, token attachment, normal/deferred/no-reply calls, timeout behavior, and disappearing named servers.
