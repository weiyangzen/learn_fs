# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sid.c

## Purpose
`samba3sid.c` implements the `samba3sid` LDB module. It auto-populates `sambaSID` on added Samba3-style `posixAccount` and `posixGroup` entries by allocating the next RID from a `sambaDomain` object's legacy RID counters.

## Important APIs, Types, And Functions
`samba3sid_next_sid()` searches all partitions for the single `sambaDomain` matching the configured SAM name, reads `sambaNextRid`, `sambaNextUserRid`, `sambaNextGroupRid`, and `sambaSID`, picks the highest available counter, increments it, builds a textual SID, and constrained-updates `sambaNextRid`. `samba3sid_add()` intercepts add requests, filters out special DNs and non-user/group object classes, skips entries that already have `sambaSID`, shallow-copies the add message, adds the generated `sambaSID`, and builds a replacement add request.

## Control Flow
On add, the module only acts for entries with `objectClass=posixAccount` or `objectClass=posixGroup` and without a supplied `sambaSID`. SID generation searches for exactly one domain object. It treats `sambaNextRid` as the previous RID, following the legacy Samba3 passdb algorithm, and updates only `sambaNextRid` after choosing the new RID. The modified add request uses `dsdb_next_callback()` to forward completion.

## State And Persistence
Persistent state is the Samba3 domain object's RID counter and the new entry's `sambaSID`. The counter update uses `dsdb_module_constrainted_update_uint32()` to guard against concurrent updates of `sambaNextRid`. The module itself has no private persistent state.

## Dependencies And Integration Points
The module depends on DSDB module search/update helpers, loadparm `lpcfg_sam_name()`, Samba security SID string conventions, and LDB add request builders. It is intended for Samba3 LDAP compatibility stacks rather than normal AD RID allocation; normal AD allocations use `ridalloc.c`.

## Risks And Test Signals
The compatibility algorithm only updates `sambaNextRid`, even when `sambaNextUserRid` or `sambaNextGroupRid` supplied the highest value, matching legacy behavior but worth preserving explicitly. It requires exactly one matching `sambaDomain`, a valid `sambaSID`, and at least one RID counter. Tests should cover supplied SID pass-through, non-user/group pass-through, missing domain, multiple domains, missing counters, constrained-update conflicts, highest-counter selection, and concurrent add attempts.
