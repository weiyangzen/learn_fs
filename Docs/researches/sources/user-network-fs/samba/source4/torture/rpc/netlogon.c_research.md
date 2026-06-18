# sources/user-network-fs/samba/source4/torture/rpc/netlogon.c

## Purpose

`netlogon.c` is the main Samba RPC torture suite for the Netlogon (`ndr_table_netlogon`) interface. It exercises secure-channel setup, credential chaining, challenge replay handling, password set/get calls, SamLogon, replication-style database APIs, domain-controller locator APIs, trust enumeration, site mapping, workstation domain-info updates, and administrative `LogonControl*` calls.

The file is not a library implementation of Netlogon. It is a broad integration test harness that drives real DC RPC endpoints using Samba torture primitives, machine credentials, generated Netlogon credentials, schannel-protected secondary pipes, and direct SAMDB/LDAP checks where needed.

## Important APIs, Types, and Functions

Key exported helpers are:

- `test_SetupCredentials()`: performs legacy `ServerReqChallenge` plus `ServerAuthenticate`, then falls back to `test_SetupCredentials2()` with AES flags if the server reports downgrade protection.
- `test_SetupCredentials2ex()`, `test_SetupCredentials2()`: perform `ServerAuthenticate2` with caller-supplied negotiation flags, computer name, secure-channel type, and expected status.
- `test_SetupCredentials3()`: performs `ServerAuthenticate3`, returns negotiated flags/RID, validates the server credential, and reissues `ServerReqChallenge` to ensure it does not disturb an established credential chain.
- `test_SetupCredentialsDowngrade()`: verifies zero negotiate flags are rejected with `NT_STATUS_DOWNGRADE_DETECTED`, then retries with ADS/AES flags.
- `test_SetupCredentialsPipe()`: duplicates the current DCERPC binding, enables `DCERPC_SCHANNEL` plus caller flags such as `DCERPC_SIGN | DCERPC_SEAL`, temporarily installs Netlogon credential state into `cli_credentials`, and opens a secured Netlogon pipe.
- `test_netlogon_ops()` and `test_netlogon_capabilities()`: shared helpers used by other tests to validate SamLogon and `LogonGetCapabilities`.

Important static test groups include challenge/authentication tests, password handling tests, SamLogon tests, replication/database API tests, DC locator/site/trust API tests, domain-info tests, async domain-info tests, and `LogonControl*` admin tests. The suite constructors are `torture_rpc_netlogon()`, `torture_rpc_netlogon_s3()`, `torture_rpc_netlogon_zerologon()`, and `torture_rpc_netlogon_admin()`.

## Control Flow

Most credential-dependent tests follow the same pattern:

1. Establish or receive a Netlogon DCERPC pipe from the torture framework.
2. Build client and server challenges with `netlogon_creds_random_challenge()` or an intentionally malformed challenge.
3. Call `dcerpc_netr_ServerReqChallenge_r()`.
4. Derive client credential state with `netlogon_creds_client_init()` from the machine password hash, challenges, secure-channel type, and negotiation flags.
5. Authenticate with `ServerAuthenticate`, `ServerAuthenticate2`, or `ServerAuthenticate3`.
6. Validate credential chaining with `netlogon_creds_client_check()` or `netlogon_creds_client_verify()`.
7. For protected calls, open a schannel pipe with `test_SetupCredentialsPipe()` and advance authenticators for each call.

The ZeroLogon-focused suite branches from this normal flow by feeding all-zero or repeated-byte challenges and by constructing password buffers that encrypt to zero-like values. It asserts `NT_STATUS_ACCESS_DENIED` or `NT_STATUS_WRONG_PASSWORD` in those paths and accepts success only for the four-byte repeated challenge boundary case.

Password tests first authenticate, then build `samr_Password` or `samr_CryptPassword` buffers, encrypt them with the negotiated Netlogon credential state and the binding auth level, call `ServerPasswordSet` or `ServerPasswordSet2`, check the return authenticator, update local `cli_credentials` to the new password/hash, and prove the change by re-authenticating.

Replication tests use a static `sequence_nums[3]` cache. `DatabaseSync()` discovers per-database sequence numbers, and `DatabaseDeltas()` consumes them to request changes. `DatabaseRedo()` iterates a large in-file table of change-log cases across SAM, BUILTIN, and LSA databases, asserting expected status, result count, and delta types.

DC locator and site tests call locator APIs with DNS and flat domain names, verify returned flags, and in some cases call `DsRGetSiteName` on the returned DC UNC. Site-address tests build IPv4 and optionally IPv6 sockaddr buffers, then repeat with too-short buffers and invalid address families to assert null site/subnet outputs.

`test_GetDomainInfo()` is stateful and multi-phase. It opens a sealed schannel pipe, optionally binds LDAP to the target DC's SAMDB, sends `LogonGetDomainInfo` with workstation OS/DNS/SPN flags, sleeps briefly for updates, checks AD attributes, then repeats with changed DNS names, missing OS fields, inbound-trust flags, null DNS hostnames, extra flags, and optionally no workstation info when dangerous tests are enabled.

Suite registration wires these functions into separate torture suites. The main suite runs broad Netlogon coverage; `netlogon-s3` is narrower and Samba3-oriented; `netlogon.zerologon` isolates CVE-2020-1472 regression tests; `netlogon.admin` tests BDC, workstation, and unauthenticated/admin `LogonControl*` behavior.

## State and Persistence Behavior

This file deliberately mutates external test state:

- Machine account passwords are changed repeatedly by `ServerPasswordSet` and `ServerPasswordSet2`; local `cli_credentials` are updated after successful changes so later tests can continue.
- `test_GetDomainInfo()` may update or verify AD attributes on the torture machine account, including `operatingSystem`, `operatingSystemServicePack`, `operatingSystemVersion`, `dNSHostName`, and `servicePrincipalName`.
- `sequence_nums[3]` is a process-global cache shared from `DatabaseSync()` to `DatabaseDeltas()`.
- Netlogon credential chains are mutable state; each authenticator call advances the chain and must be verified against the returned authenticator.
- Temporary secondary pipes are created for schannel, LSA-over-Netlogon, and DC locator stress paths and then released via talloc ownership.

The tests assume a disposable torture machine account named `torturetest`. Running these against a non-disposable account or production DC would be risky.

## Dependencies and Integration Points

The file depends on Samba's torture framework, generated NDR clients for Netlogon and LSA, libcli credential/auth helpers, Netlogon credential crypto helpers, event handling, command-line credentials, loadparm configuration, LDB/SAMDB access, socket address definitions, and DCERPC binding APIs.

Important integration points include machine-account torture testcase creation, generated `dcerpc_*_r()` calls, async `dcerpc_netr_LogonGetDomainInfo_r_send/recv()`, direct SAMDB validation with `ldb_wrap_connect()` and `gendb_search()`, and LSA-over-Netlogon tests through `dcerpc_secondary_auth_connection()`.

## Risks and Edge Cases

The highest-risk areas are the ones the tests intentionally stress: credential downgrade handling, challenge reuse across pipes/global caches, zero/repeated challenge rejection, all-zero encrypted password buffers, empty machine passwords, ARC4/AES negotiation differences, return-authenticator chain advancement, and AD state updates from workstation info.

Environment sensitivity is high. Some branches skip or loosen expectations for Samba3/Samba4 settings, native mode servers, dangerous tests, local transports, lack of IPv6, Windows behavior around empty passwords, and unimplemented Netlogon APIs.

There is a notable implementation hazard in `test_GetDomainInfo_async()`: it calls `test_SetupCredentials3(p, ...)` before `p` is assigned, even though the function parameter is `p1`. Since `test_SetupCredentials3()` returns false when passed `NULL`, this path appears to fail before opening the schannel pipe unless surrounding build or call context masks it. That should be reviewed before relying on async coverage.

The tests print generated passwords in torture comments. This is acceptable for disposable torture accounts but is a logging risk if run with real machine credentials.

## Test Signals

Passing signals include exact NTSTATUS/WERROR assertions, successful credential-chain checks, expected `ServerAuthenticate*` downgrade or denial statuses, successful re-authentication after password mutations, expected database delta counts/types, expected DC locator flags, expected site/subnet nulling for invalid addresses, and AD attribute matches after `LogonGetDomainInfo`.

Failing signals are intentionally precise: unexpected `NT_STATUS_OK` for forbidden ZeroLogon-style inputs, mismatched return authenticators, unsupported AES negotiation when required, changed DNS/SPN state when it should stick, unexpected `LogonControl*` access/error codes, or inability to reconnect with newly set machine credentials.
