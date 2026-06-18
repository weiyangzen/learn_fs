<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.c

## Purpose
This file provides low-level synchronous SAMR and LSA RPC helper functions used by winbind domain backends. It enumerates users and groups, resolves group and alias membership, enumerates trusted domains, and translates SID arrays through LSA lookup calls.

## Important APIs, Types, And Functions
User and group enumeration is handled by `rpc_query_user_list()`, `rpc_enum_dom_groups()`, and `rpc_enum_local_groups()`. Membership helpers include `rpc_lookup_usergroups()`, `rpc_lookup_useraliases()`, `rpc_lookup_groupmem()`, and `rpc_lookup_aliasmem()`. Trust discovery is in `rpc_trusted_domains()`. SID lookup uses `rpc_lookup_sids()` with an NCACN-IP-TCP fast path through `rpc_try_lookup_sids3()`.

## Control Flow
Enumeration functions loop on `STATUS_MORE_ENTRIES`, reallocating result arrays and appending returned entries. Membership functions open SAMR user, group, or alias handles, call the relevant query RPC, close temporary handles, and compose returned RIDs into full domain SIDs or formatted names. `rpc_trusted_domains()` first tries `EnumTrustedDomainsEx`, falls back to older `EnumTrustDom`, and builds `netr_DomainTrust` entries. `rpc_lookup_sids()` connects to LSAT and uses `LookupSids3` over TCP transport or `LookupSids` for other transports, then validates translated-name/domain indexes.

## State And Persistence Behavior
There is no durable state. Result arrays are talloc-owned by the caller context, while temporary RPC arrays, policy handles, and stack frames are freed before return. Remote state is read-only except for opening and closing RPC policy handles.

## Dependencies And Integration Points
The file depends on generated SAMR/LSA client stubs, Samba RPC pipe clients, `cli_samr`, `cli_lsarpc`, SID helpers, and winbind name formatting utilities. It is consumed by `winbindd_samr.c` and other RPC-backed winbind code that already holds connected SAMR/LSA pipes and policy handles.

## Risks And Test Signals
Important risks are off-by-one and overflow handling while appending paged RPC results, stale policy handles, invalid server responses where returned counts do not match request counts, and trust enumeration fallback behavior. `rpc_trusted_domains()` has a particularly sensitive mixed `dom_list_ex`/`dom_list` path; tests should cover both modern and legacy LSA servers. Good signals are SAMR enumeration tests, alias membership tests with more than 1024 SIDs, LSAT lookup tests over named pipe and TCP, and leak/error-path checks for handle closes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.c -->
