# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diffreg.c

Regular-file diff algorithm implementation. The header comment documents Harold Stone’s longest common subsequence approach.

Core data structures are global arrays of line hashes, sorted line records, equivalence classes, candidate chains, match vector `J`, and line offsets. `prune` removes common prefix/suffix from consideration. `sort` shell-sorts line hashes. `equiv` builds equivalence classes of equal line hashes in file 1. `unsort` restores file 0 equivalence indexes to original order.

`stone` walks file 0 equivalence classes to build k-candidates for the longest common subsequence, using `search` and `newcand`. `unravel` converts the candidate chain into the match vector `J`, restoring pruned prefix/suffix matches. `output` scans `J` to call `change` for additions/deletions/changes, in reverse order for ed-script mode.

`cmp` compares binary files byte-for-byte in buffered chunks. `diffreg` orchestrates opening/preparing files, binary path, pruning/sorting/equivalence/LCS, verification with `check`, output, and cleanup.

Integration points: called by `main.c` for regular files; uses `diffio.c` for prepare/check/change output.

Risks and notes: memory is manually overlaid/reused between arrays to reduce footprint, making ownership subtle. The line hash can collide, but `check` corrects false matches. There is a typo in the fallback S_ISREG macro area in unrelated conditional macros, but the file’s own logic does not use those macros.
