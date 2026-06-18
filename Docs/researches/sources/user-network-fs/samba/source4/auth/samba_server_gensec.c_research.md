# sources/user-network-fs/samba/source4/auth/samba_server_gensec.c

Purpose: central server-side GENSEC bootstrap used by Samba services that authenticate against local Samba configuration and SAM resources.

Important APIs: `samba_server_gensec_start()` creates default `gensec_settings` from loadparm, creates an `auth4_context`, starts a server GENSEC context, attaches server credentials, and optionally sets the target service. `samba_server_gensec_krb5_start()` builds a constrained backend list containing Kerberos5 and SPNEGO before calling the common setup helper.

Control flow: callers pass event/messaging/loadparm contexts and server credentials. The private helper allocates a temporary context, calls `auth_context_create()`, then `gensec_server_start()`, applies credentials and service name, and steals the resulting `gensec_security` into the caller context. Public wrappers reparent the settings object below the returned context so backend settings survive for the GENSEC lifetime.

State/dependencies/integration: no durable state; lifetime state is talloc-owned GENSEC settings, backend arrays, auth context, credentials, and target-service metadata. Integrates `auth4`, `gensec`, server credentials, loadparm GENSEC settings, tevent, and imessaging so services get consistent server authentication setup.

Risks/test signals: backend restriction in the Kerberos variant depends on successful `gensec_init()` and OID lookup. Ownership is subtle: freeing settings too early would break the returned context. No direct unit test in this subset; coverage comes from subsystem users and Kerberos/GENSEC selftests.
