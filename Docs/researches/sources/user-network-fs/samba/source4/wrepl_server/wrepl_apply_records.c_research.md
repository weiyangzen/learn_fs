<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_apply_records.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_apply_records.c

## Purpose

This file applies WINS replication records received from a partner to the local WINS database. It implements the WREPL conflict-resolution matrix for unique, normal group, special group, and multi-homed names across owned and replica records, including replacement, propagation, challenge, release-demand, and merge actions.

## Important APIs, Types, and Functions

- `enum _R_ACTION` represents the selected action: replace, not replace, propagate, challenge, release demand, or special-group merge.
- Address-list helpers compare old `winsdb_record` addresses with incoming `wrepl_name` addresses.
- `replace_*_replica_vs_X_replica()` and `replace_*_owned_vs_X_replica()` encode the conflict matrix.
- `r_do_add()`, `r_do_replace()`, `r_not_replace()`, `r_do_propagate()`, `r_do_mhomed_merge()`, `r_do_challenge()`, `r_do_release_demand()`, and `r_do_sgroup_merge()` execute selected actions.
- `wreplsrv_apply_one_record()` chooses an action for one incoming record.
- `wreplsrv_apply_records()` applies a batch and updates the local owner table.

## Control Flow

For each incoming `wrepl_name`, `wreplsrv_apply_one_record()` truncates overlong scopes to Windows-compatible length, looks up the local record, and adds a new record if absent. If present, it classifies the conflict as same owner, replica-vs-replica, or local-owned-vs-replica. Static records get special protection/propagation handling. Otherwise, type-specific matrix functions select an action. The action dispatcher modifies the WINS DB, starts an async challenge through the local `nbt_server` IRPC interface, sends release demands, or merges address lists.

After the batch, `wreplsrv_apply_records()` updates `service->table` with the remote owner max version using `wreplsrv_add_table()`.

## State and Persistence Behavior

The file persists changes in `winsdb`: adds records, replaces records, allocates new version IDs, takes ownership, deletes/updates address lists through modifications, and updates owner-table state. Challenge and release-demand operations are asynchronous IRPC calls to `nbt_server`; their states are talloc-stealed to the partner/service until completion.

## Dependencies and Integration Points

It depends on WREPL NDR types, WINS DB record APIs, NBT name utilities, IRPC bindings to `nbtd_proxy_wins_challenge` and `nbtd_proxy_wins_release_demand`, tevent, loadparm option `wreplsrv:propagate name releases`, and partner/service structures from `wrepl_server.h`. It is called by outbound pull cycles after receiving name batches.

## Risks and Edge Cases

The conflict matrix is large and maintenance-sensitive. Some action names/comments contain typos but not behavior changes. Asynchronous challenge/release-demand results are mostly best-effort, so failures may leave temporary inconsistencies. `r_do_release_demand()` keeps a reference to the old address list before replacement; lifetime correctness depends on talloc ownership. Special-group merge behavior can intentionally diverge from Windows when `propagate name releases` is enabled. Scope truncation mutates incoming names before DB lookup.

## Test Signals

Signals include correct WINS DB state after all matrix cases, allocated versions when local ownership/propagation is required, release demands after replacing local unique/mhomed records with group/sgroup records, successful mhomed/sgroup merges, and updated owner-table max versions after a batch. WREPL/NBT torture tests should catch regressions in conflict outcomes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_apply_records.c -->
