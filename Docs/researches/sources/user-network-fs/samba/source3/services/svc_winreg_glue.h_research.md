# sources/user-network-fs/samba/source3/services/svc_winreg_glue.h

Purpose: public header for service-control registry glue helpers.

Important functions and APIs: forward-declares `struct auth_session_info` and declares `svcctl_gen_service_sd`, `svcctl_get_secdesc`, `svcctl_set_secdesc`, `svcctl_get_string_value`, `svcctl_lookup_dispname`, and `svcctl_lookup_description`. The prototypes expose `messaging_context`, `auth_session_info`, `TALLOC_CTX`, `security_descriptor`, `WERROR`, and boolean success conventions.

Control flow: header-only; describes callable operations implemented in `svc_winreg_glue.c`.

State and persistence: documents the interface to persistent registry-backed service descriptors and metadata, but holds no state itself.

Dependencies and integration: included by svcctl server code and `svc_winreg_glue.c`. Callers must provide auth/session context because registry access is security-scoped.

Risks and test signals: pointer ownership is talloc-based and must be respected by callers, especially for returned strings and descriptors allocated on `mem_ctx`. Compile-time consistency and svcctl RPC tests are the main signals.
