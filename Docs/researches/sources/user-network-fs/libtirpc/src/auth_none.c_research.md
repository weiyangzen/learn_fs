<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_none.c -->
# sources/user-network-fs/libtirpc/src/auth_none.c

Purpose: Implements singleton AUTH_NONE credentials for unauthenticated RPC calls.

Important APIs, types, and functions: Exports `authnone_create`; implements marshal, no-op verifier, validate, refresh, destroy, wrap/unwrap, and static op-vector setup.

Control flow: First call allocates singleton private storage, initializes null credential/verifier, pre-marshals both opaque auth records into a fixed buffer, and returns the singleton AUTH. Marshal copies the cached bytes into the target XDR stream.

State and persistence behavior: Global singleton `authnone_private` persists for process lifetime; destroy is intentionally no-op. Mutexes protect initialization and cached marshal access.

Dependencies and integration points: Depends on XDR opaque auth, `_null_auth`, and libtirpc mutex globals.

Risks: Singleton lifetime means memory is intentionally never freed, which is normal but can appear as a leak. `authnone_refresh` always false, so callers must handle auth refresh failure correctly.

Test signals: Indirectly exercised by RPC clients using default/no auth; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_none.c -->
