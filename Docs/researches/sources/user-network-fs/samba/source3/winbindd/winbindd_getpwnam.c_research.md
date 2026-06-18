# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwnam.c

## Purpose
Implements async `WINBINDD_GETPWNAM`, resolving a username to a `struct winbindd_pw` passwd response.

## Important APIs, Types, And Control Flow
The send path copies the username, runs `wb_parent_idmap_setup_send()`, unmaps normalized names through `NormalizeNameUnmap`, parses namespace/domain/user, and performs `wb_lookupname_send()` with `LOOKUP_NAME_NO_NSS`. The lookup callback treats `SID_NAME_UNKNOWN` as unmapped and calls `wb_getpwsid_send()` for the resolved SID. `winbindd_getpwnam_done()` receives the passwd record, and recv copies `state->pw` into `response->data.pw`.

## State And Persistence
Only request-local state plus indirect idmap setup initialization. No database writes.

## Dependencies And Integration Points
Uses parent idmap setup, idmap child normalization, `parse_domain_user`, `wb_lookupname`, `wb_getpwsid`, generated wbint normalization stubs, and lookup flags from passdb.

## Risks And Test Signals
Risks include NSS recursion if flags change, normalization/unmap mismatches, malformed domain-user syntax, and no explicit SID type filtering before `wb_getpwsid`. Test domain-qualified, UPN, normalized, unmapped, computer/user names, malformed strings, idmap child failures, and long passwd fields.
