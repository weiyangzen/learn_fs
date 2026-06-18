## sources/sync-backup/bup/lib/bup/rm.py

Purpose: removes backup branches or individual saves by rewriting branch history and updating Git refs atomically at the end of the operation.

Important APIs and control flow: `dead_items(repo, paths)` resolves VFS paths and classifies requests into whole branches (`RevList`) and saves (`Commit`), rejecting `latest`, ordinary files, inaccessible paths, and mixed invalid inputs. `rm_saves()` computes commits to drop and calls `filter_branch()`, which walks the branch history oldest-to-newest and copies non-excluded commits through `append_commit()`. `bup_rm()` builds `updated_refs`, writes replacement commits with `PackWriter` for save removal, then performs `git.delete_ref()` or `git.update_ref()`.

State, dependencies, and integration: state changes are Git refs and new local pack objects. It depends on VFS resolution, `git.rev_list`, `git.catpipe`, `get_commit_items`, `LocalPackStore`, and error collection in `bup.helpers`. It integrates with GC because removed refs leave now-unreachable objects that `bup gc` later prunes.

Risks and tests: history rewriting assumes all selected saves are on one branch and that `filter_branch()` can find at least one removed commit. Ref updates are attempted per ref, so partial failure is possible after generated pack data exists. Direct tests are outside this subset (`test-rm*`), while this subset’s `test-gc` and `test-fsck` exercise branch deletion effects and orphaned pack cleanup after `bup rm --unsafe`.
