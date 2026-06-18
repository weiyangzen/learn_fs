# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/Authenticator.java

Purpose: `Authenticator` defines the session-setup authentication strategy interface.

Important APIs and control flow: `init(SmbConfig)` prepares per-authenticator state, `supports(AuthenticationContext)` selects compatible contexts, and `authenticate(context, gssToken, connectionContext)` consumes a server token and returns the next token/session key response or `null` when complete.

State, dependencies, and integration: implementations are created through named factories configured in `SmbConfig`, selected by `SMBSessionBuilder`, and may be stateful across token exchanges.

Risks: the interface assumes one authenticator instance per session setup; sharing instances would corrupt state. Tests should use fake authenticators to verify selection, multi-step token exchange, and failure propagation.
