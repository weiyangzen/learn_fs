<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.h -->
# sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.h

Purpose: public declarations for Samba's Kerberos context wrapper.

Important APIs and types: `struct smb_krb5_context` holds the raw `krb5_context`, private log data, and current tevent context. `smb_krb5_init_context_basic()` returns a raw initialized krb5 context configured for Samba. `smb_krb5_init_context()` returns the talloc-managed wrapper. Heimdal builds also expose callback typedefs for send-to-realm and send-to-KDC functions plus event-context install/remove helpers.

Control flow and state: the header defines ownership: callers receive a talloc-owned wrapper whose destructor frees the krb5 context. Heimdal event helpers temporarily associate a tevent loop with Kerberos network operations and restore previous state after use.

Dependencies and integration: requires krb5 types, talloc, tevent, and loadparm declarations. Included by `kerberos.h`, credential helpers, and GENSEC Kerberos code.

Risks and test signals: build tests need MIT, system Heimdal, and embedded Heimdal configurations. Runtime tests should ensure callers do not outlive referenced event contexts and that nested Kerberos operations restore the previous `current_ev`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.h -->
