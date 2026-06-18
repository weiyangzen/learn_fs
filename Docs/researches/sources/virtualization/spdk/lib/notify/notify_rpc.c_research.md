# File Research: sources/virtualization/spdk/lib/notify/notify_rpc.c

JSON-RPC query interface for SPDK notifications.

Key RPCs:
- `notify_get_types`: accepts no parameters and returns an array of registered notification type names.
- `notify_get_notifications`: accepts optional `id` and `max`, then returns notification objects with `type`, `ctx`, and `id`.

Dependencies:
- SPDK RPC, notify, string/env/util/log, and RPC autogen contexts.

Research notes:
- The RPC layer is read-only; event production is through `spdk_notify_send`.
- Defaults `max` to `UINT64_MAX`, leaving the underlying 1024-event ring as the real upper bound.
- Scope relevance: management API for polling SPDK event notifications.
