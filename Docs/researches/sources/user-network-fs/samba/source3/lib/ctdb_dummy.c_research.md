# sources/user-network-fs/samba/source3/lib/ctdb_dummy.c

Purpose: provides non-cluster stub implementations for CTDB/messaging/dbwrap symbols so Samba can link without CTDB support.

Important APIs/types/functions: stubs for `ctdbd_probe()`, CTDB messaging registration/IP functions, `ctdbd_process_exists()`, `db_open_ctdb()`, `messaging_ctdb_send()`, `messaging_ctdb_ref()`, `messaging_ctdb_register_tevent_context()`, `messaging_ctdb_connection()`, and `ctdb_async_ctx_reinit()`.

Control flow: functional calls return `ENOSYS`, `NULL`, or `false`; deregistration/unregister/pass functions are no-ops.

State and persistence: no state or persistence.

Dependencies/integration: includes the same public CTDB, messaging, dbwrap, and torture headers as callers expect, preserving ABI at link time when clustering is disabled.

Risks/test signals: callers must gate CTDB behavior on cluster support or handle `ENOSYS`/null cleanly. Tests should build without cluster support and verify local database paths do not call these stubs unexpectedly, while explicit cluster-only operations fail with clear unsupported errors.
