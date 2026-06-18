# sources/user-network-fs/samba/source3/param/loadparm_ctx.c

Purpose: adapts Samba3's global loadparm implementation to the shared/Samba4 `loadparm_context` helper interface.

Important APIs and flow: private wrappers `lp_service_for_s4_ctx()`, `lp_servicebynum_for_s4_ctx()`, and `lp_load_for_s4_ctx()` add short-lived talloc stackframes around S3 calls. Static `s3_fns` fills a `struct loadparm_s3_helpers` with function pointers for parameter pointer lookup, service lookup, loading, command-line storage, dumping, include processing, LDAP debug initialization, section parsing, and global initialization. `loadparm_s3_helpers()` refreshes `helpers->globals` and `helpers->flags` before returning the singleton helper table.

State and persistence: no durable state; it bridges to `loadparm.c` global state. The helper struct is static and mutable only for its state pointers.

Dependencies and integration: includes `lib/param/s3_param.h` and is consumed by `loadparm_init_s3()` callers, including Python module creation and `loadparm.c` setup contexts.

Risks: returns pointers to global services after freeing only the temporary stackframe; correctness relies on those services being globally owned. The singleton helper table is not isolated per context, so concurrent or nested uses share global state.

Test signals: creating S3-backed contexts, loading without reinit, dumping, include callbacks, and Python `get_context()` should exercise this bridge.
