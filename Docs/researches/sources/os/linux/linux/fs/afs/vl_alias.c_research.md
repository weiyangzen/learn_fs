# File Research: sources/os/linux/linux/fs/afs/vl_alias.c

## Scope

This file detects when a newly discovered AFS cell is an alias of an already known cell by querying YFS canonical cell names or comparing sampled volume/server/address data.

## Public And Internal APIs Covered

- `afs_cell_detect_alias()` is the external alias-detection entry point.
- Internal helpers sample volumes, compare fileserver address lists and volume server lists, compare `root.cell`, query known volumes in other cells, and request YFS canonical cell names.

## Control Flow And Behavior

- The preferred path asks YFS VL servers for the canonical cell name. If it differs from the requested name, the canonical cell is looked up and installed as `cell->alias_of`.
- If YFS canonical naming is unsupported, the code samples `root.cell` and compares it against root volumes of existing non-alias cells.
- Cells without `root.cell` are compared by picking an existing volume from another known cell, looking for a same-named volume in the candidate cell, then comparing volume IDs, server UUID lists, and endpoint address lists.
- Address-list comparison treats matching RxRPC peer pointers as evidence that fileservers overlap.
- Detection is serialized by `net->cells_alias_lock` and clears `AFS_CELL_FL_CHECK_ALIAS` after a non-error decision.

## State And Data Structures

- Uses `cell->alias_of`, `cell->root_volume`, per-net `proc_cells`, and per-cell volume RB trees.
- Temporary sampled volumes are ordinary `afs_volume` records obtained through `afs_create_volume()`.

## Dependencies

- Volume creation, VL cursor rotation, YFS VL `GetCellName`, cell lookup, RCU traversal, and per-cell/per-net locks.

## Risks And Invariants

- Alias detection can perform network lookups and may return `-ERESTARTSYS`.
- Comparing volumes relies on stable sorted server lists and shared peer objects for address matches.
- `alias_of` transfers a held cell reference on success.
