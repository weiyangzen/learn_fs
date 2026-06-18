# sources/user-network-fs/nfs-utils/systemd/rpc-gssd.service.in

Purpose: This template unit runs `rpc.gssd`, the RPC security service for NFS client and server Kerberos/GSS use.

Important APIs and control flow: It has no default dependencies, conflicts with unmount, requires and starts after `rpc_pipefs.target`, checks for `@_sysconfdir@/krb5.keytab`, is `PartOf=nfs-utils.service`, and starts `/usr/sbin/rpc.gssd` as a forking service.

State, dependencies, and integration: Template substitution supplies the sysconfdir. Runtime state lives in rpc_pipefs and Kerberos credential/keytab infrastructure.

Risks and test signals: Keytab condition suppresses the service for keyless or gssproxy-only setups. Tests should verify substitution, rpc_pipefs ordering, restart via nfs-utils, and behavior with missing keytab.
