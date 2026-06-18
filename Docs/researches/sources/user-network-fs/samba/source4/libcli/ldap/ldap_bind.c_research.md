# sources/user-network-fs/samba/source4/libcli/ldap/ldap_bind.c

Purpose: implements LDAP simple bind, SASL/GENSEC bind, and rebind for Samba's LDAP client connection.

Important APIs: `ldap_rebind()`, `ldap_bind_simple()`, and `ldap_bind_sasl()`. Internal constructors create simple and SASL LDAP bind messages.

Control flow: simple bind chooses explicit or cached DN/password, sends a BindRequest, waits, validates a BindResponse, and caches simple credentials for later rebind. SASL bind requires an active socket, empty send queue, and no pending requests, initializes GENSEC, chooses wrapping/channel binding behavior based on TLS, anonymous credentials, and loadparm settings, starts `GSS-SPNEGO`, loops over `gensec_update()` and LDAP SASL BindRequests until complete, handles stronger-auth and invalid-credential retries, validates sign/seal features, and wraps the raw tstream with a GENSEC tstream when negotiated.

State and persistence: stores bind type and credentials pointer in `conn->bind`; stores `conn->gensec`; may switch `conn->sockets.active` to SASL stream. No disk persistence.

Dependencies and integration: depends on LDAP message/request APIs, TLS channel binding, GENSEC, credentials, loadparm, packet/tstream wrappers, and ADS auth flags. Security integration is central.

Risks: SASL bind is intentionally serialized against pending traffic; bypassing this would corrupt stream state. Credential feature mutation is temporarily applied and restored, so failure paths must not tattoo caller credentials. Channel binding behavior is configurable for testing and must be handled carefully. Test signals include simple bind defaults, SASL over TLS with channel bindings, sign/seal requirements, strong-auth retry, invalid-credential retry, empty-output final GENSEC step, and failure cleanup of `conn->gensec`.
