# sources/user-network-fs/samba/source4/torture/rpc/lsa_lookup.c

## Purpose

This file is a focused LSARPC lookup torture test for `LookupSids`. Unlike the broader `lsa.c`, it targets cross-domain and well-known SID translation behavior, including a required outgoing NT4/downlevel trust. It verifies how lookup levels map well-known, BUILTIN, local-domain, and trusted-domain SIDs, and it includes a regression test for the reply shape when a SID is not mapped.

## Important APIs, Types, and Functions

The file uses generated `dcerpc_lsa_*` client stubs, Samba SID utilities, and RPC torture setup helpers. Important helpers are `open_policy()`, `get_domainsid()`, `lookup_sids()`, `test_lookupsids()`, `get_downleveltrust()`, `torture_rpc_lsa_lookup()`, `test_LookupSidsReply()`, and `torture_rpc_lsa_lookup_sids()`.

`open_policy()` opens an LSARPC policy handle with `OpenPolicy2` and `SEC_FLAG_MAXIMUM_ALLOWED`. `get_domainsid()` reads `LSA_POLICY_INFO_DOMAIN`. `get_downleveltrust()` enumerates trusted domains and queries `QueryTrustedDomainInfoBySid` level 6, selecting an outgoing downlevel trust. `lookup_sids()` wraps `lsa_LookupSids`, and `test_lookupsids()` asserts both returned status and per-SID type array.

## Control Flow

`torture_rpc_lsa_lookup()` connects to LSARPC, accepts only named-pipe or local transports, opens a policy, gets the local domain SID, finds a trusted downlevel SID, and builds an eight-entry SID list: Everyone, Interactive, BUILTIN domain, BUILTIN Users, local domain, local Domain Admins RID 512, trusted domain, and trusted Domain Admins RID 512. It then invokes `test_lookupsids()` for lookup levels 0 through 10, asserting invalid-parameter results for unsupported levels and specific mapping/unmapping behavior for valid levels.

`test_LookupSidsReply()` is a separate suite entry. It looks up a synthetic domain-admin SID under a fabricated domain SID and expects `NT_STATUS_NONE_MAPPED`, while still asserting that the returned names array has one element and preserves the string form of the unmapped SID. A disabled `#if 0` block documents Windows-version disagreement around returned domain lists.

## State and Persistence Behavior

This file does not create or delete server objects. It only opens a policy handle and reads domain/trust data. The main persistent dependency is external: the target server must already have an outgoing downlevel/NT4 trust for `get_downleveltrust()` to succeed. All client memory is talloc-scoped to the torture context.

## Dependencies and Integration Points

It depends on LSARPC policy/query/lookup calls, the local domain SID, a trusted-domain inventory, SID parsing/duplication/RID helpers, and transport filtering via `dcerpc_binding_handle_get_transport()`. The exported suite `torture_rpc_lsa_lookup_sids()` registers a single `LookupSidsReply` test under the LSARPC interface.

## Risks and Edge Cases

The main operational risk is that this test is topology-specific. Without an outgoing trust to an NT4/downlevel domain, `get_downleveltrust()` calls `torture_fail()`. The expected SID type arrays encode subtle LSARPC lookup-level semantics, especially which well-known and trusted-domain SIDs are intentionally unmapped at levels 2, 3, 4, and 6. The reply-shape test allows for historical Windows differences by not enforcing the domain list assertions.

## Test Signals

Success signals are exact NTSTATUS comparisons for each lookup level and exact `enum lsa_SidType` comparisons for each SID when the status allows per-name inspection. Additional signals include transport gating, successful policy open, successful domain SID query, discovery of a suitable downlevel trust, and verification that a none-mapped lookup still returns a populated names array with the expected string.
