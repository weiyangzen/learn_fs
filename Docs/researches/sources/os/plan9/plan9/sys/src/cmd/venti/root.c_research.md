# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/root.c

Purpose: inspect Venti root blocks.

Behavior:
- Accepts one or more root scores.
- Reads each as `VtRootType`, validates size equals `VtRootSize`, unpacks `VtRoot`, and prints score, quoted name/type, data score, block size, and previous score.
- Continues after per-score parse/read/unpack failures.

Integration points:
- Uses `quotefmtinstall`, Venti score formatting, `vtread`, and `vtrootunpack`.

Risks:
- Hard-coded diagnostic text says wrong size `!= 300`, matching historical `VtRootSize`.
