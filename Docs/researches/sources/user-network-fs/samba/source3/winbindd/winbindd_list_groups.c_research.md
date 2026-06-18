# sources/user-network-fs/samba/source3/winbindd/winbindd_list_groups.c

## Purpose
Implements async `WINBINDD_LIST_GROUPS`, returning comma-separated fully qualified group names across all domains or one requested domain.

## Important APIs, Types, And Control Flow
`winbindd_list_groups_send()` respects `WBFLAG_FROM_NSS` plus `lp_winbind_enum_groups()` by returning an empty success when NSS enumeration is disabled. It selects either the requested domain or all domains from `domain_list()`, stores each as a `winbindd_domain_ref`, and fires parallel `dcerpc_wbint_QueryGroupList_send()` calls through each domain child handle. `winbindd_list_groups_done()` receives each domain result, validates the domain ref, logs and suppresses per-domain failures by zeroing that domain's group count, and completes after all subrequests return. Recv first computes output length using `fill_domain_username_talloc()`, then builds a comma-separated string and sets `num_entries`.

## State And Persistence
Only request-local arrays of domain refs and returned `wbint_Principals`. It may initialize/contact domain children indirectly through wbint calls but writes no persistent data.

## Dependencies And Integration Points
Uses domain list/ref APIs, generated wbint QueryGroupList, `dom_child_handle()`, winbind enum group configuration, and the internal `_wbint_QueryGroupList()` server.

## Risks And Test Signals
If zero groups are returned, `result[len-1] = '\0'` underflows because `len` is zero; empty-domain and enumeration-disabled paths need attention. Other risks include partial-domain failure being hidden, stale domain refs, and large output memory use. Test no domains, one empty domain, NSS enum disabled, requested unknown domain, mixed success/failure domains, and very large group lists.
