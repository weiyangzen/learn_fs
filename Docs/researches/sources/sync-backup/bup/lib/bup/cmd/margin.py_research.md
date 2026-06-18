# sources/sync-backup/bup/lib/bup/cmd/margin.py

## Purpose
`margin.py` analyzes object ID distribution in the repository, reporting either the longest matching SHA1 prefix or prediction error for object offset distribution.

## APIs and Control Flow
`main(argv)` rejects positional arguments, checks the repo, opens `git.PackIdxList` with optional `ignore_midx`, and writes to stdout. In `--predict` mode `do_predict` compares each object's sorted position to its expected position from the first 64 hash bits. Default mode scans adjacent IDs, computes the maximum bit-prefix match using `_helpers.bitmatch`, and logs collision-capacity estimates.

## State, Dependencies, Integration, Risks, Tests
It is read-only. Dependencies include pack index iteration, `_helpers.bitmatch`, and math/struct calculations. It is diagnostic rather than core backup flow. Risks include division by zero for an empty object list, stale earth-population constant in explanatory output, and precision assumptions for very large indexes. Test signals include no-arg enforcement, midx vs idx-only selection, duplicate object skipping, predict output formatting, and behavior on small/empty repositories.
