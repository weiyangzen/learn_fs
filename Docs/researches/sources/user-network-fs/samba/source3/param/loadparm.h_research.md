# sources/user-network-fs/samba/source3/param/loadparm.h

Purpose: public Samba3 loadparm header exposing the S3 configuration API to daemons, passdb, smbd, Python helpers, and the shared loadparm bridge.

Important APIs/types: forward declares `loadparm_context`, `loadparm_service`, `files_struct`, `smbd_server_connection`, and security descriptor types. It declares initialization/helpers (`loadparm_s3_init_globals()`, `loadparm_s3_helpers()`), substitution/accessors, parametric readers, service creation/removal/lookup, registry/usershare loaders, config load variants, dump APIs, role/security/protocol derived getters, spoolss/sendfile/mangling controls, widelinks helpers, and `get_globals()`/`get_flags()` style state access through the helper implementation.

State and persistence: the header itself owns no state but exposes functions that operate on process-global configuration, service arrays, usershare state, registry/file backends, and command-line sticky settings.

Dependencies and integration: includes `talloc.h` and `regex.h`; depends on generated enum/type declarations available through wider Samba includes. It is the contract used by `service.c`, `loadparm_ctx.c`, nmbd modules, passdb, and tests.

Risks: because this header publishes many process-global mutators, API additions can lock in global-state assumptions. Callers must respect ownership of returned talloc strings versus const internal pointers. Signature drift must stay synchronized with `loadparm.c` and generated `param_functions.c`.

Test signals: compile coverage across all consumers is the primary signal. ABI/API-sensitive changes should be validated by full source3 builds and by loadparm unit/smoke tests.
