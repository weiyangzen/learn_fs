# File Research: sources/os/linux/linux-stable/fs/afs/vl_alias.c

## Scope

Detects when a newly discovered AFS cell is an alias of an already known cell.

## APIs And Behavior

- Samples volumes in a candidate cell with `afs_create_volume()`.
- Compares root or sampled volume IDs, sorted server UUID lists, and fileserver address-list peer matches.
- For YFS VL servers, queries the canonical cell name and resolves it to an existing/master cell when it differs.
- Falls back to comparing `root.cell` volume data, or querying arbitrary known volumes in cells without `root.cell`.
- `afs_cell_detect_alias()` serializes alias detection and records `cell->alias_of` on success.

## State And Dependencies

Uses cell volume rb-trees, proc cell list, root-volume cache, volume/server/address-list comparisons, VL cursor RPCs, and cell lookup refs. It depends on volume creation and server-list address discovery being sufficiently complete for comparison.

## Risks And Invariants

Alias detection is heuristic unless YFS canonical names are available. The code avoids aliasing against cells already marked as aliases and transfers cell references into `alias_of` on success.
