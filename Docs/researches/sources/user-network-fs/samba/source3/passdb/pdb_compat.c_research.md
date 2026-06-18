# sources/user-network-fs/samba/source3/passdb/pdb_compat.c

## Purpose

`pdb_compat.c` provides compatibility helpers for older RID-centric passdb callers. It converts between full user/group SIDs and RIDs using the current global SAM SID, delegating actual SID storage to `pdb_get_set.c` setters.

## Important APIs

`pdb_get_user_rid()` and `pdb_get_group_rid()` extract RIDs from `pdb_get_user_sid()` and `pdb_get_group_sid()` if the SID belongs to `get_global_sam_sid()`. `pdb_set_user_sid_from_rid()` and `pdb_set_group_sid_from_rid()` compose full SIDs from the global SAM SID and call `pdb_set_user_sid()` or `pdb_set_group_sid()`.

## Control Flow, State, And Integration

All four functions guard against null `struct samu` inputs. Setters fetch the global SAM SID, compose a domain SID plus RID with `sid_compose()`, set the result with the requested `enum pdb_value_state`, and log the full SID at debug level 10. Getters return `0` if the input is null or the stored SID does not share the current global SAM SID. The file depends on `passdb.h`, SID helpers, and the global SAM SID from `machine_sid.c`; it is used by account initialization, serialization/deserialization, algorithmic RID code, and legacy backend interfaces.

## Risks And Test Signals

The zero return from RID getters can mean invalid input or a real RID-like zero, so callers must treat it carefully. If the global SAM SID cache is stale, conversions can fail or compose incorrect SIDs. Tests should cover null inputs, non-domain SIDs, valid user/group RID extraction, setter flag propagation, and behavior after `reset_global_sam_sid()`.
