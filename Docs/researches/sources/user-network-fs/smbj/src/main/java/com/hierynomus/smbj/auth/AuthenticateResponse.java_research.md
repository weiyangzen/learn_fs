# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticateResponse.java

Purpose: `AuthenticateResponse` is the mutable handoff object returned by authenticators during session setup.

Important APIs and control flow: it carries a SPNEGO token, session key, Windows version, NetBIOS name, and NTLM negotiate flags. Constructors allow an empty response or token-initialized response.

State, dependencies, and integration: `SMBSessionBuilder` serializes `negToken`, stores `sessionKey`, and copies server metadata into `ConnectionContext`. NTLM and SPNEGO authenticators populate different fields.

Risks: byte arrays and negotiate flag sets are not defensively copied, so callers can mutate secrets or flags after publication. Tests should verify each authenticator populates required fields for each authentication phase and handles null session keys.
