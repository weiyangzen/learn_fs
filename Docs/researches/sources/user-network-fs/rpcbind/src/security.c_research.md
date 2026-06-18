<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/security.c -->
# sources/user-network-fs/rpcbind/src/security.c

Purpose: Centralizes rpcbind access control, caller locality checks, verbose audit logging, and remote-call deny rules for sensitive RPC programs/procedures.

Important APIs, types, and functions: Exports `check_access`, `is_loopback`, `is_localroot`, `logit`, and `check_callit`. It defines constants for sensitive NFS, mountd, YP, ypbind, yppasswd, and rquota programs/procedures. With `LIBWRAP`, it integrates TCP wrappers through `request_info`, `hosts_access`, and severity globals. Logging severity defaults to auth/info for normal verbose logs and auth/warning for denials.

Control flow: `check_access` inspects the RPC procedure and denies SET/UNSET from non-loopback callers unless `insecure` is set. Other procedures pass this local-only gate. It then applies TCP wrappers for non-AF_LOCAL callers when enabled. Verbose logging records accepted and denied requests via `logit`. `check_callit` allows NULLPROC, denies indirect calls to rpcbind unless insecure, denies selected mountd/YP/NFS/rquota operations, and logs denial.

State and persistence: No persistent state. It reads global runtime options `insecure`, `oldstyle_local`, `debugging`, and `verboselog`. `logit` forks for syslog work so DNS/RPC name lookup does not block the daemon; `reap` in `rpcbind.c` collects those children.

Dependencies and integration points: Consumes caller addresses from `svc_getrpccaller`, depends on `rpcbind.h` request structures, uses `xlog` for debug, and integrates with the shared service code that calls access checks before serving procedures. Local-root behavior relies on AF_LOCAL or loopback with reserved source ports when `oldstyle_local` is enabled.

Risks: `oldstyle_local` disables IPv4/IPv6 loopback recognition when false but always treats AF_LOCAL as local. Reserved source port checks are legacy trust signals and should not be treated as strong authentication. `logit` forks per event, so verbose logging under high traffic can create process churn. TCP wrappers only see socket addresses and are bypassed for AF_LOCAL.

Test signals: Test SET/UNSET from AF_LOCAL, IPv4 loopback, IPv6 loopback, and remote addresses with `insecure` on/off and `oldstyle_local` on/off. Test `check_callit` deny matrix for NFS, mountd mount/unmount, ypbind setdom, selected YP calls, and rpcbind self-calls. With `LIBWRAP`, use allow/deny fixtures and verify log severity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/security.c -->
