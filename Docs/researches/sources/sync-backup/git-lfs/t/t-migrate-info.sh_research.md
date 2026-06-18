# sources/sync-backup/git-lfs/t/t-migrate-info.sh

Purpose: read-only reporting coverage for `git lfs migrate info`. It verifies that the command summarizes candidate migration data by file pattern, size, count, percentage, pointer-following mode, threshold, top-N limit, units, and `--fixup` semantics without rewriting refs.

Important APIs/functions: sources `fixtures/migrate.sh` and `testlib.sh`; uses the same migration fixtures as import tests, then compares `git lfs migrate info` output with here-doc expectations via `diff -u`, `tail`, `wc`, and `grep`. It uses `assert_ref_unmoved` around `git rev-parse` snapshots to enforce read-only behavior.

Control flow: tests set up local, remote, bare, tracked, corrupt-tracked, nested, alternate-name, and symlinked-attribute repositories. Each test runs `git lfs migrate info` with options such as explicit refs, `--include`, `--exclude`, `--include-ref`, `--exclude-ref`, `--skip-fetch`, `--above`, `--top`, `--unit`, `--everything`, `--pointers=follow|no-follow|ignore`, and `--fixup`, then compares only the relevant output tail or validates an empty result.

State/persistence behavior: no migration state should be persisted. The suite repeatedly records `HEAD`, local branches, feature branches, and remote refs before and after reporting. It also validates that failure cases, such as symlinked `.gitattributes` or invalid refs/options, leave tree and ref state unchanged.

Dependencies/integration points: exercises Git revision traversal, Git attribute matching, LFS pointer parsing, report aggregation, size formatting, tracked-versus-untracked file classification, remote ref discovery, and command-line validation. `--fixup` specifically depends on attribute evaluation to identify files that should already be LFS pointers but are not.

Risks/test signals: failures show as output drift, incorrect aggregation, read-only commands moving refs, bad pointer-following semantics, or bad validation for incompatible options. Because many tests assert tabular formatting exactly, legitimate presentation changes need coordinated test updates.
