# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticationContext.java

Purpose: `AuthenticationContext` stores username, password, and domain for NTLM-style authentication.

Important APIs and control flow: constructor copies the provided password into an internal `char[]`; factories create anonymous and guest contexts. `isAnonymous` and `isGuest` are used by authenticators and signing logic to choose flags and session behavior.

State, dependencies, and integration: fields are final, but `getPassword()` returns the internal array. `SmbFileSystemProvider` creates instances from URI/env values, and `NtlmAuthenticator` consumes them.

Risks: returning the password array exposes mutable secret state, and `username` may be null if callers pass null. Tests should cover defensive construction, anonymous/guest detection, URI-derived values, and string representation not leaking passwords.
