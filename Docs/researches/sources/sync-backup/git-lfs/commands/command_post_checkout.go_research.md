<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_checkout.go -->
# sources/sync-backup/git-lfs/commands/command_post_checkout.go

Purpose: implements the `post-checkout` hook command that enforces read-only permissions for lockable files after checkout operations.

Important APIs/types/functions: `postCheckoutCommand`, `postCheckoutRevChange`, and `postCheckoutFileChange`; `newLockClient`, `locking.Client.GetLockablePatterns`, `FixLockableFileWriteFlags`, `FixAllLockableFileWriteFlags`, and `git.GetFilesChanged`.

Control flow: validates the three Git hook args, returns if lockable read-only mode is disabled or no lockable patterns exist, then distinguishes branch/SHA checkout from file checkout. Revision changes try to diff old/new commits and fix only changed files, falling back to full scan on diff failure; file checkout performs a full lockable scan.

State and persistence behavior: mutates working-tree file permissions according to lock ownership and lockable patterns. It may query local/remote lock state through the lock client depending on client internals.

Dependencies/integration points: installed by Git LFS hooks, depends on Git hook argument contract, lock client patterns, and Git version.

Risks and test signals: risks include full-repo scan cost, fallback after diff errors, hook failures logged as warnings rather than hard stops, and zero SHA handling only for initial checkout. Test signals include branch checkout, file checkout, disabled setting, no lockable patterns, diff failure fallback, and permission changes for locked/unlocked files.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_post_checkout.go -->
