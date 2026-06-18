# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.c

## Role

Run-length encoded memory device wrapper. It attempts to store scan lines as runs until operations require standard uncompressed memory representation.

## Important Warning

The file states: “THIS CODE HAS NOT BEEN TESTED.” This should be treated as a major maintenance and reliability note.

## Main API

- `gdev_run_from_mem(gx_device_run *rdev, gx_device_memory *mdev)` converts a memory device to run-length form if enough runs fit in each scan line.

## Data Model

- Each line begins with a `run_line` header followed by an array of `run` entries.
- Runs are held in a doubly linked list with dummy start and end runs.
- Uninitialized lines store `zero` as the device white value and avoid constructing run lists.
- `smin/smax1` tracks ranges converted back to standard form.
- `umin/umax1` tracks a range of uninitialized lines.

## Main Behavior

- `gdev_run_from_mem` saves original memory device procedures and replaces drawing/get-bits operations with run-aware trampolines.
- Most rendering operations call `run_standardize`, expanding affected lines back to normal memory form, then delegate to saved procedures.
- `run_fill_rectangle` is the main optimized operation; it fills intervals in run form when possible.
- `run_fill_interval` splits, deletes, inserts, and merges runs around a replacement interval.
- If a line runs out of run entries, it is standardized and the fill delegates to the original memory fill.

## Risks and Edge Cases

- Untested by the authors.
- Complex bitfield packing limits run count and length.
- Mutates the same scan-line storage between run metadata and expanded pixel data.
- The large run manipulation code has nontrivial cursor and free-list invariants.
