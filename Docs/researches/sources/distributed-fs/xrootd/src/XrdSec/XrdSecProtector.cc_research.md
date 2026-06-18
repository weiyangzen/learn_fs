# sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtector.cc

Purpose: Provides the default request-protection factory exported as `XrdSecProtObjectP` and manages server/client creation of `XrdSecProtect` instances.

Important APIs and functions: `Config` converts local/remote `XrdSecProtectParms` into `ServerResponseReqs_Protocol` templates. `LName` maps levels to strings. `New4Client` creates a client object from server response requirements. `New4Server` selects local versus remote policy and clones a configured template. `ProtResp` returns the correct response payload for a client address.

Control flow: Server startup configures local and remote policies, creates template `XrdSecProtect` objects when levels are non-none, and sets shortcut globals. Runtime server creation chooses local/remote by `XrdNetIF::InDomain`, honors relaxed old-client behavior, checks whether the authentication protocol has an encryption key, and either disables, warns, or forces unencrypted digest behavior. Client creation validates response length and requires either encryption support or forced mode.

State and persistence: Namespace globals `lrTab`, `lrSame`, and `noProt` hold process-wide protection policy. Template protection objects are heap allocated and persist. No disk persistence.

Dependencies and integration points: Links with `XrdNetIF`, `XrdSecProtect`, `XrdSecInterface`, `XrdSysError`, and XRootD protocol structs. It is loaded by `XrdSecLoadProtection`.

Risks: Policy is global and not guarded for reconfiguration; it assumes startup-only configuration. `ProtResp` ignores the `pver` argument, so compatibility relies on `New4Server` relaxed checks. Lack of encryption downgrades protection unless `force` is set. Local/remote split depends on correct `Entity.addrInfo`.

Test signals: Configure all levels, local-only and remote-only policies, relaxed old-client protocol levels, forced and non-forced no-key protocols, local-domain detection, `ProtResp` sizes, and client validation of vector lengths.
