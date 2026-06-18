# sources/user-network-fs/nfs-ganesha/src/include/gss_credcache.h

Purpose: This header declares GSS/Kerberos credential cache management functions imported from the gssd-style credential refresh layer.

Important APIs/types/functions: `struct gssd_k5_kt_princ` is forward declared for keytab principal data. Global `ccachesearch[]` lists credential cache search locations. Public functions initialize, shut down, and clear the credential cache, verify mechanisms with `gssd_check_mechs`, and refresh machine credentials with `gssd_refresh_krb5_machine_credential`.

Control flow: Ganesha's GSS/RPC security startup initializes the cache, checks available mechanisms, refreshes machine credentials from keytabs/principals, and clears/shuts down during lifecycle events.

State and persistence: Credential cache state is external Kerberos/GSS state, potentially backed by filesystem or memory caches. The header controls access but does not define storage.

Dependencies and integration points: Includes BSD queue, RPC/GSS, Kerberos, and GSSAPI headers. Integrates with NFS_KRB5 configuration, RPCSEC_GSS callbacks, and machine credential renewal.

Risks: Credential cache paths and keytab principal handling are security-sensitive. Refresh failures can break secure NFS callbacks. Build depends on Kerberos/GSS headers and ABI compatibility with imported gssd structures.

Test signals: Build with GSS support, initialize/shutdown repeatedly, validate mechanism detection, refresh credentials for valid and invalid keytabs/principals, clear caches, and exercise secure NFS callback authentication.
