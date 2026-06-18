# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diffreg.c

Regular-file diff engine using the classic Harold Stone longest common subsequence approach over hashed lines.

Key behavior:
- `prune` removes common prefix/suffix ranges from the expensive comparison window.
- `sort`, `equiv`, and `unsort` organize equal line hashes into equivalence classes.
- `stone` builds candidate chains for the longest common subsequence; `unravel` converts the selected chain into match vector `J`.
- `cmp` byte-compares binary files after `prepare` marks input as binary.
- `calcdiff` orchestrates input preparation, pruning, sorting, equivalence construction, LCS computation, match verification, and offset table creation.
- `output` converts `J` gaps into `change` calls, using reverse order for ed-script mode.
- `diffreg` owns a temporary `Diff` instance and `freediff` releases open buffers and generated arrays.

Notable dependencies:
- `prepare`, `check`, `change`, and `flushchanges` from `diffio.c`.
- Memory helpers from `util.c`.

Research notes:
- The implementation overlays storage aggressively, matching the long file comment’s goal of minimizing memory.
- `unsort` uses plain `malloc` without an allocation check, unlike most code in this command.
- Binary differences print `binary files <file1> <file2> differ` and skip text hunk output.
