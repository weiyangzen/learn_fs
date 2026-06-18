<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file_research.md`. Source lines read for this pass: 75.

## Purpose
Rewrites files, symlinks, or directories in place so eCryptfs re-encrypts contents or filenames under current mount options.

## Important APIs, Types, And Functions
No shell functions beyond `error`; arguments are paths to rewrite. Uses `mktemp`, `cp -a`, and `mv -T`.

## Control Flow
Iterates over paths, skips missing entries and `.`, renames directories through a temporary name, or copies files/symlinks to a temporary peer and renames back over the original. Counts successful rewrites and exits nonzero if any failed.

## State And Persistence Behavior
Mutates target paths in place and creates temporary peer files/directories. The intended persistent effect is newly encrypted lower contents or filename metadata.

## Dependencies And Integration Points
Depends on shell, gettext, `mktemp`, `cp`, `mv`, and an active eCryptfs mount.

## Risks And Edge Cases
In-place rewrite can lose metadata or data on interruption, especially around copy/rename failures. Directories are renamed rather than deep-copied, so callers must avoid racing users.

## Test Signals
Test by changing eCryptfs options or keys, rewriting representative files/dirs/symlinks, unmounting/remounting, and verifying data and lower-name changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-rewrite-file -->
