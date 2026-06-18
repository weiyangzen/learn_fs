<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_util.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos_util.c

Purpose: implements Kerberos credential, principal, ccache, and keytab utility functions used across source4 authentication.

Important APIs and types: `struct principal_container` wraps a `krb5_principal` with an `smb_krb5_context` and talloc destructor. `principal_from_credentials()` and the static impersonation helper parse principal strings from `cli_credentials`. `smb_krb5_create_principals_array()` creates krb5 principals from SPNs plus an account/realm principal. `kinit_to_ccache()` obtains tickets into an existing ccache using passwords, S4U2Self/S4U2Proxy-style impersonation, or an RC4 keyblock from an NT hash. `smb_krb5_get_keytab_container()`, `smb_krb5_remove_obsolete_keytab_entries()`, and `smb_krb5_is_exact_entry_in_keytab()` manage keytab handles and entries.

Control flow: principal parsing allocates wrapper state before calling krb5 so cleanup is simple. Ticket acquisition builds get-init-creds options, sets forwardable and canonicalization behavior, optionally configures FAST armor, wraps Heimdal KDC I/O with the caller's tevent context, tries twice for clock-skew recovery, updates krb5 real time when needed, and may retry after wrong-password callbacks refresh credentials. Keytab cleanup enumerates entries, compares against target principals and kvno, releases cursors before deletion, and restarts enumeration after deletion.

State and persistence: krb5 principal and keytab lifetime is tied to talloc destructors. `kinit_to_ccache()` mutates the supplied ccache and may adjust the krb5 context's time offset. Keytab helpers persist changes in the keytab file or memory keytab.

Dependencies and integration: depends on Samba credentials, Kerberos credential wrappers, Heimdal/MIT macros, libkrb5, loadparm, tevent, and Samba keytab comparison helpers. It is called by GENSEC Kerberos, keytab export/update code, and credential cache acquisition.

Risks and test signals: FAST support is feature-macro dependent and returns EINVAL if required but unavailable. S4U impersonation requires a password, not only a keyblock. Keytab kvno comparison masks to 8 bits to handle file formats, so tests must include kvno wraparound. Ticket acquisition tests should cover password, NT-hash keyblock, FAST, skew, wrong-password refresh, missing principal, and cleanup of krb5 objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos_util.c -->
