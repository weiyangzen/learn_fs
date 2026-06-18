# sources/user-network-fs/samba/source3/passdb/machine_sid.c

## Purpose

`machine_sid.c` manages the process-wide cached local SAM SID, including generating or migrating it when no valid secrets entry exists. The local SAM SID equals the domain SID only when Samba is acting as a DC; otherwise it is the workstation SID.

## Important APIs And Functions

The public API is `get_global_sam_sid()`, `reset_global_sam_sid()`, `sid_check_is_our_sam()`, and `sid_check_is_in_our_sam()`. Private helpers include `read_sid_from_file()` for old `MACHINE.SID` compatibility, `generate_random_sid()` for `S-1-5-21-x-y-z` SID creation, and `pdb_generate_sam_sid()` for discovery/migration/generation.

## Control Flow, State, And Persistence

`get_global_sam_sid()` returns cached `global_sam_sid` if available. On first use it opens `secrets_db_ctx()`, starts a dbwrap transaction, calls `pdb_generate_sam_sid()`, and commits. It panics on missing secrets DB, transaction failure, or SID generation failure because Samba cannot safely continue without a stable local SAM SID.

`pdb_generate_sam_sid()` checks DC state first: a DC prefers the workgroup domain SID. It then tries the local netbios-name SID. For DCs, mismatches between local and domain SID are repaired by storing the domain SID under the local name; missing domain SID is populated from local SID. If no secrets SID exists, it reads and migrates `$private_dir/MACHINE.SID`, unlinks the file after storing, and for non-DCs also stores the same SID under the workgroup. Finally it generates and stores a random SID; DCs store it as both local and workgroup domain SID. `reset_global_sam_sid()` frees the in-memory cache so later callers requery secrets.

## Dependencies And Integration Points

This file depends on `passdb/machine_sid.h`, `secrets.h`, `dbwrap`, security SID helpers, loadparm values such as `lp_workgroup()`, `lp_netbios_name()`, and `lp_private_dir()`, and the `IS_DC` role macro. Its result is used throughout passdb for RID composition, SID membership checks, user/group lookup, and account serialization.

## Risks And Test Signals

Startup races are mitigated with a secrets DB transaction. Incorrect role detection or mismatched stored SIDs can cause identity drift, so the DC repair logic is critical. Tests should cover fresh generation, DC and non-DC storage keys, migration from `MACHINE.SID`, unlink-after-migration, mismatched DC local/domain SID repair, cache reset after store, transaction failure behavior, and `sid_check_is_in_our_sam()` stripping a RID before comparison.
