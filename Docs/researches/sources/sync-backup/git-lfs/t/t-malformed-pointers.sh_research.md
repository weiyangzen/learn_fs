# sources/sync-backup/git-lfs/t/t-malformed-pointers.sh

## Purpose

Tests clone/smudge behavior when Git blobs match LFS-tracked attributes but are malformed or empty pointer candidates. It ensures malformed data is preserved as normal file content and empty blobs remain empty without noisy clone logging.

## Important APIs, control flow, and dependencies

The tests create remotes, track `*.dat`, disable LFS process/clean filters while adding files, generate malformed blobs of 1023, 1024, 1025, and 1048576 bytes with `lfstest-genrandom`, commit and push them, clone another repo, and compare source and cloned file contents. The empty case adds an empty `.dat` blob with filters disabled and checks blob and worktree byte counts.

## State, dependencies, integration points, risks, and test signals

State includes Git blobs that are not valid LFS pointers, clone logs, and worktree files. Integration points are pointer parser size limits, smudge filter fallback behavior, clone logging, and clean-filter bypass configuration. Risks include treating arbitrary tracked blobs as pointers, corrupting malformed files during checkout, or logging empty blobs as pointer errors. Signals are clone log greps for malformed files, exact content equality, zero-byte checks, and absence of empty-file clone log entries.
