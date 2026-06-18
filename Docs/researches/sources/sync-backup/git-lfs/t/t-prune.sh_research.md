# sources/sync-backup/git-lfs/t/t-prune.sh

Purpose: large integration suite for `git lfs prune`, covering when local LFS objects may be deleted and which references must retain them.

Important APIs/functions: uses remote/clone fixtures, `lfstest-testutils addcommits`, `calc_oid`, `assert_local_object`, `refute_local_object`, `assert_server_object`, `git lfs prune` flags `--dry-run`, `--verify-remote`, `--verbose`, `--recent`, and `--force`, plus Git stash, index, branch, remote, config, and diff controls.

Control flow: tests cover old unreferenced object deletion, all paths excluded by fetch filters, unpushed commits, recent refs/commits, remote reachability, remote verification including large ref counts, unreachable refs, stashed worktree/index/untracked data, `--recent`, index-retained files, force pruning with repeated runs, empty files, external diff avoidance, and long-line diff/stash-diff hang prevention. Each scenario builds specific commits and object OIDs, tunes `lfs.fetchrecentrefsdays`, `lfs.fetchrecentremoterefs`, `lfs.fetchrecentcommitsdays`, or fetch include/exclude settings, runs prune, and validates retained/deleted local objects and sometimes server objects.

State/persistence behavior: mutates `.git/lfs/objects` by pruning, while preserving objects reachable from current refs, recent refs, unpushed commits, stashes, indexes, and configured retention windows. It also checks behavior against remote object availability and local Git diff configuration.

Dependencies/integration points: integrates Git ref traversal, reflog/recent logic, remote LFS batch verification, stash representation, index parsing, path filters, prune dry-run accounting, filesystem object deletion, and protection against invoking external diff/textconv programs.

Risks/test signals: failures risk data loss by deleting needed LFS objects, disk bloat by retaining too much, hangs on pathological diffs, or incorrect trust in remote availability. Count and OID assertions are extensive and intentionally conservative.
