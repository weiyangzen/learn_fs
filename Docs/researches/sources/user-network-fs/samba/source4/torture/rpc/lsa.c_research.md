# sources/user-network-fs/samba/source4/torture/rpc/lsa.c

## Purpose

This file is Samba's broad RPC torture coverage for the LSARPC interface. It exercises policy handle creation, name/SID lookup paths, policy information queries, LSA account and privilege APIs, secret storage, trusted-domain creation/deletion, trust password authentication, and exported torture suites for focused `lsa.lookupnames`, `lsa.trusted.domains`, and `lsa.privileges` runs. It is not a server implementation; it is an integration test client that validates Samba or Windows LSARPC behavior over DCE/RPC transports.

The file has two operating modes. Over named pipes or local RPC it opens policy handles and runs mutating server-state tests. Over TCP it expects unauthenticated or insufficiently protected handle-less calls such as `LookupSids3`, `LookupNames4`, `OpenPolicy*`, and `GetUserName` to fail unless a secure authenticated channel is present.

## Important APIs, Types, and Functions

The primary external APIs are generated NDR client stubs from `ndr_lsa_c.h`, `ndr_netlogon_c.h`, and shared RPC helpers from `torture/rpc/torture_rpc.h`. Security and identity data flows through `struct policy_handle`, `struct dom_sid`, `struct lsa_String`, `struct lsa_TransNameArray`, `struct lsa_SidArray`, `union lsa_PolicyInformation`, `union lsa_TrustedDomainInfo`, `struct cli_credentials`, and Netlogon credential state.

The file exposes helper entry points used by other torture code: `test_lsa_OpenPolicy2_ex()`, `test_lsa_OpenPolicy2()`, `test_lsa_OpenPolicy3_ex()`, `test_lsa_OpenPolicy3()`, `test_many_LookupSids()`, `test_lsa_Close()`, `torture_rpc_lsa()`, `torture_rpc_lsa_get_user()`, `torture_rpc_lsa_lookup_names()`, `torture_rpc_lsa_trusted_domains()`, and `torture_rpc_lsa_privileges()`.

Core local test families include policy opening, `LookupNames`/`LookupSids` variants, account and privilege management, secret creation/query/update/delete, trusted-domain enumeration and creation, Netlogon trust-password checks, and optional Heimdal Kerberos referral validation.

## Control Flow

`torture_rpc_lsa()` connects to `ndr_table_lsarpc`, branches on transport, and then either runs TCP failure/secure-channel checks or the full named-pipe/local suite. In the full path it opens policy handles, joins a temporary workstation account named `lsatestmach`, runs async and bulk SID lookup tests, policy info queries, secret mutation tests, lookup round trips, close semantics, leaves the joined domain, and finally validates `GetUserName`.

Lookup flow is intentionally round-trip based. SID lookups populate translated-name arrays; the translated names are immediately fed into name lookup calls to verify both directions agree. The `LookupSids3`/`LookupNames4` logic also branches on transport and authentication metadata: secure schannel or Kerberos privacy over TCP may succeed, while insecure contexts should return access-denied/protseq failures.

The trusted-domain suite opens LSARPC policy handles, creates multiple synthetic trusts, verifies enumeration/query behavior, and deletes them by SID. The extended variants repeat creation through `CreateTrustedDomainEx`, `CreateTrustedDomainEx2`, and `CreateTrustedDomainEx3`. `test_CreateTrustedDomainEx_common()` chooses trust direction, trust type, and RC4 encryption attributes in a pattern, encrypts or marshals auth info according to the RPC variant, checks created metadata, optionally verifies trust authentication, and then enumerates and removes all created trusts.

Trust password validation is multi-protocol. `check_dom_trust_pw()` creates incoming credentials for domain or DNS-domain secure channels, resolves the target DC, performs Netlogon pings, authenticates with `ServerAuthenticate3`, optionally establishes a signed/sealed Netlogon pipe, updates the trust password with `ServerPasswordSet2`, and reauthenticates with the new password/version. When Heimdal support is compiled in, `check_pw_with_krb5()` installs a custom send-to-KDC hook, forces KDC traffic to the target realm, checks canonicalization/referral results, validates expected Kerberos errors, inspects referral-ticket kvnos and encryption, and covers two-, three-, and four-part service principals.

## State and Persistence Behavior

This test file deliberately mutates the target server. It creates and deletes LSA accounts, creates local and global secrets with random names, joins and leaves a temporary machine account, and creates/deletes many trusted-domain objects. Cleanup is attempted inline after each object family, but interrupted runs can leave `torturesecret-*`, `G$torturesecret-*`, `TORTURE*`, or `lsatestmach` artifacts on the test server.

Client-side state is mostly talloc-scoped to the torture context. Policy handles are opened and closed explicitly, and `test_lsa_Close()` asserts double-close context mismatch behavior. Kerberos state uses a memory ccache and a destructor for `check_pw_with_krb5_ctx` to free principals, creds, tickets, keyblocks, addrinfo, and options. The file relies on random names and IDs for collision avoidance, but some trust and SID strings are deterministic; collisions trigger best-effort deletion/recreation in trust creation paths.

## Dependencies and Integration Points

The file integrates generated LSARPC and Netlogon clients, DCE/RPC binding/transport helpers, talloc memory ownership, tevent async RPC, Samba security SID utilities, LSA init helpers, Netlogon credential helpers, Kerberos utilities, resolver APIs, and GnuTLS crypto headers. Test behavior is controlled by torture settings such as `samba3`, `samba4`, `binding`, and `host`, and by transport type (`NCACN_NP`, `NCALRPC`, or `NCACN_IP_TCP`).

The suite assumes server support for LSARPC policy operations and, for trust-auth tests, a domain-controller environment with Netlogon and Kerberos reachable. Some branches explicitly skip or relax expectations for Samba3, Samba4, MIT Kerberos builds, or unimplemented server calls.

## Risks and Edge Cases

The highest risk is environmental flakiness: trust creation, Kerberos referral assertions, Netlogon pings, and secure-channel setup depend on domain topology, DNS/NetBIOS resolution, transport security, and server policy. The test contains many Windows-version compatibility allowances; tightening them without checking actual Windows/Samba behavior may introduce false failures.

The mutating tests are risky in shared environments because they modify LSA objects and trust passwords. Cleanup is present but not transactional. `test_CreateTrustedDomainEx_common()` creates 12 trusts per variant in the exported suite, and failures before deletion can leave persistent trust entries. Secret tests depend on transport session keys and encrypted buffer behavior; incorrect session-key handling can produce confusing server-side status codes such as `UNKNOWN_REVISION`.

Kerberos validation has compile-time bifurcation between embedded Heimdal and MIT builds, and some assertions differ by cache/referral behavior. Any refactor must preserve those conditional expectations.

## Test Signals

Primary pass/fail signals are `torture_assert_*`, `torture_fail()`, `torture_skip()`, and accumulated boolean `ret` values. Important status expectations include `NT_STATUS_OK`, `STATUS_SOME_UNMAPPED`, `NT_STATUS_NONE_MAPPED`, `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_RPC_PROTSEQ_NOT_SUPPORTED`, `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE`, `NT_STATUS_OBJECT_NAME_COLLISION`, `NT_STATUS_NO_MORE_ENTRIES`, `STATUS_MORE_ENTRIES`, and Kerberos-specific error codes. Strong signals include lookup round-trip consistency, correct policy info level support, secret new/old value and mtime behavior, trust enumeration resume-handle monotonicity, trusted-domain metadata equality, Netlogon credential chaining, trust password rollover, and Kerberos referral-ticket content.
