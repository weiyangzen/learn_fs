# sources/user-network-fs/samba/source3/lib/ldap_debug_handler.c

Purpose: routes LDAP/LBER library debug output into Samba logging where supported.

Important APIs/types/functions: `init_ldap_debugging()` and conditional `samba_ldap_log_print_fn()`.

Control flow: supported builds install the LBER log print callback; unsupported builds compile to a no-op.

State/persistence behavior: modifies process-global LBER library option state only.

Dependencies/integration: depends on LDAP build features, `smb_ldap.h`, and Samba debug logging.

Risks/test signals: platform-dependent callback signatures are the main risk. Build matrix and LDAP debug smoke tests validate behavior.
