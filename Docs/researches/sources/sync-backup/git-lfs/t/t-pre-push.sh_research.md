# sources/sync-backup/git-lfs/t/t-pre-push.sh

Purpose: comprehensive integration suite for the Git LFS pre-push hook, which decides which LFS objects must be uploaded before Git refs are pushed and enforces missing-object, locking, redirect, remote, and optimization behavior.

Important APIs/functions: uses `git lfs pre-push`, normal `git push`, `git lfs push --dry-run`, `git lfs track`, `assert_server_object`, `refute_server_object`, `assert_local_object`, lock helpers, fixture HTTP status injection for locks verification, remote setup/clone helpers, and explicit stdin-style ref lines for hook invocation.

Control flow: early tests feed good, tracked, and bad refs to `git lfs pre-push`, then compare real push, dry-run, and skip-push behavior. Upload tests cover redirects, existing objects, untracked existing server objects, missing local objects with default rejection, allowed incomplete push modes, multiple branches, bad remotes, deleted remote branches after server GC, branch deletion, and force-pushed refs. Lock tests cover own locks, other users' locks on LFS and non-LFS lockable files, multiple HTTP status codes for lock verification, and URL-scoped config disabling. Later tests cover `pushDefault`, remote URL optimization, avoiding traversal for objects the server already has, and local-path remotes.

State/persistence behavior: the suite mutates local LFS object storage, server-side object storage, Git refs, branch tracking config, lock records, remote URLs, and LFS config such as `lfs.allowincompletepush` and locksverify settings. It verifies both positive uploads and negative non-uploads.

Dependencies/integration points: integrates Git pre-push hook stdin protocol, LFS transfer queue, batch API, locks verification API, HTTP redirects/statuses, ref negotiation, remote URL matching, server object existence checks, and Git branch deletion/force-push behavior.

Risks/test signals: failures can block valid pushes, allow Git refs to move without required LFS objects, ignore locks, upload to wrong endpoints, or do excessive object traversal. Several cases depend on exact stderr/log text and fixture HTTP behavior.
