<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_server_service.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_server_service.c

Purpose: minimal service module initializer for the auth service.

Important API: `server_service_auth_init(TALLOC_CTX *ctx)` simply calls `auth4_init()` to register built-in auth4 modules when the Samba service subsystem initializes the internal `service_auth` module.

Control flow and state: there is no per-request state. The only runtime effect is triggering auth backend static initialization through `auth4_init()`, which is idempotent in `auth.c`.

Dependencies and integration: depends on `auth/auth.h` and is declared as an internal `service` subsystem module by the NTLM wscript. It ensures authentication backends are ready during server startup.

Risks and test signals: tests are startup/build oriented: loading `service_auth` should register expected auth backends exactly once and tolerate repeated initialization. Failures here would surface as missing auth backends in services rather than direct auth errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_server_service.c -->
