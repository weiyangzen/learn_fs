# sources/user-network-fs/impacket/tests/dcerpc/test_raa.py

Purpose: tests Remote Authorization API (`raa`) context creation, compound contexts, access checks, context information queries, and claim/SID modification reachability.

Important APIs and functions: `RAATests` binds `raa.MSRPC_UUID_RAA` over TCP with packet privacy. `get_account_sid()` resolves the configured username to a SID through LSAT/LSAD over `\PIPE\lsarpc` and caches it at class level. `setUp()` uses `epm.hept_lookup()` to find the RAA TCP port from a non-nil object UUID registration. `build_security_descriptor()` constructs a self-relative security descriptor with one allow ACE granting `GENERIC_ALL` to a SID. Tests cover raw/helper `AuthzrInitializeContextFromSid`, `AuthzrFreeContext`, `AuthzrInitializeCompoundContext`, `AuthzrAccessCheck`, `AuthzGetInformationFromContext`, `AuthzrModifyClaims`, and `AuthzrModifySids`.

Control flow: setup resolves account SID and dynamic port before each test. Context tests create one or two authorization contexts, call the target operation, then free all handles. Access-check tests create a context, build an in-memory security descriptor, pass it as `SR_SD`, and free the context. Modify-claims/SIDs tests assert a server-side session error while ensuring the call reaches the server.

State and persistence behavior: remote state is not changed. It creates transient authorization context handles and frees them. Class-level `account_sid` cache persists within the test process.

Dependencies and integration points: integrates EPM, LSAT/LSAD SID lookup, LDAP security descriptor classes, and RAA object UUID request dispatch. Requires RAA registered over TCP and sufficient rights to resolve the user's SID.

Risks: setup skips tests if RAA is not registered or SID resolution fails. Security descriptor construction is low-level and can regress with LDAP type changes. The override calls `super(DCERPCTests, self).setUp()`, which intentionally bypasses `DCERPCTests.setUp()` and may be brittle.

Test signals: validates dynamic object-endpoint lookup, SID resolution, self-relative security descriptor encoding, authorization context lifecycle, compound context handling, access-check replies, and expected errors for modify operations.
