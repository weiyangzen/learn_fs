# sources/distributed-fs/xrootd/src/XrdSecunix/XrdSecProtocolunix.cc

Purpose: simple Unix identity security protocol plugin that sends effective user and group names as credentials.

Important APIs and functions: local class `XrdSecProtocolunix` implements `Authenticate()`, `getCredentials()`, and `Delete()`. Exports `XrdSecProtocolunixInit()` and `XrdSecProtocolunixObject()` for the XRootD security plugin ABI.

Control flow: client `getCredentials()` creates a buffer beginning with `"unix"`, appends effective username and optional group name, and returns `XrdSecCredentials`. Server `Authenticate()` accepts empty credentials as host identity, verifies the `"unix"` protocol ID, duplicates the credential string, splits username and group on spaces, and fills `XrdSecEntity`. Object creation stores endpoint host/address.

State and persistence: per-instance state is endpoint address, allocated host string, and duplicated credential buffer. No persistence, no cryptographic state, and init returns empty parameters.

Dependencies and integration: uses `XrdOucUtils::UserName()` and `GroupName()`, `XrdNetAddrInfo`, `XrdSecInterface`, and XRootD version/export macros.

Risks: this protocol does not authenticate cryptographically; it trusts client-supplied username/group and is appropriate only in trusted/local contexts. Credential parsing is space-delimited, so unusual names are not supported. Empty credentials map to `prot=host` and name `"?"`.

Test signals: plugin load, credential generation for known euid/egid, server parse with and without group, protocol mismatch error, empty credential handling, and leak checks for repeated authentication.
