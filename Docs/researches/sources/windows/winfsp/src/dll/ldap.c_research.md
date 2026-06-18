# File Research: sources/windows/winfsp/src/dll/ldap.c

This file wraps a small subset of Windows LDAP APIs used by WinFsp.

Key responsibilities:
- `FspLdapConnect` initializes an LDAP connection, enables signing/encryption, and binds with negotiated authentication.
- `FspLdapClose` unbinds the connection.
- `FspLdapGetValue` performs a synchronous search for one attribute and copies the first value into WinFsp-allocated memory.
- `FspLdapGetDefaultNamingContext` reads `defaultNamingContext` from the root DSE.
- `FspLdapGetTrustPosixOffset` searches trusted domain records under `CN=System,<context>` and returns `trustPosixOffset`, matching by flat name or DNS-style name.

Filesystem relevance:
- Supports identity mapping / domain trust integration for POSIX uid/gid behavior in Windows environments.
- No filesystem dispatch logic is here; it is directory-service support.
