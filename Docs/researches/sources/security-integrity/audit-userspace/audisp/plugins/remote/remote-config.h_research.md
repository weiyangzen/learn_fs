# sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.h

Purpose: declares remote plugin configuration enums and structure.

Important APIs and data: defines modes, transports, formats, failure actions, overflow actions, and `remote_conf_t` fields for endpoint, queue, retry, heartbeat, Kerberos, and action executables.

Control flow: no implementation; enums drive parser and runtime switch statements.

State and persistence: structure holds process-local parsed config with heap-owned strings.

Dependencies and integration: used by both parser and remote daemon. Kerberos principal is mutable because GSS setup rewrites slash to `@`.

Risks: enum values such as TLS/labeled transport are declared but not implemented by current transport initialization. Ownership of `const char *` fields is mixed but freed by `free_config`.

Test signals: compile-time coverage and parser/runtime switch tests for each enum.
