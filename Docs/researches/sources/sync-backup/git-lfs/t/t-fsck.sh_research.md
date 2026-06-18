# sources/sync-backup/git-lfs/t/t-fsck.sh

## Purpose

Comprehensive coverage for `git lfs fsck` object and pointer validation. It checks default repair behavior, dry-run behavior, shell-character paths, outside-repo errors, malformed/noncanonical pointers, Git object directory overrides, no-object cases, symlink and negated attribute exemptions, object corruption/missing files, excluded paths, explicit refs/ranges, and invalid refs.

## Important APIs, control flow, and dependencies

Helper functions `create_invalid_pointers`, `setup_invalid_pointers`, and `setup_invalid_objects` build repositories with tracked data, CRLF/noncanonical pointer blobs, large non-pointer blobs added with LFS filters disabled, corrupted object files, and removed object files. Tests run `git lfs fsck`, `--dry-run`, `--pointers`, `--objects`, explicit refs/ranges, and commands under `GIT_WORK_TREE`, `GIT_DIR`, and `GIT_OBJECT_DIRECTORY`.

## State, dependencies, integration points, risks, and test signals

State includes `.git/lfs/objects`, `.git/lfs/bad`, Git blobs, `.gitattributes` and macro attributes, symlinks, excluded paths, and alternate object directories. Integration points are pointer parser canonicalization, attribute matching and negation, local object hash verification, repair movement, ref walking, shell-safe path handling, and object-directory plumbing. Risks include moving files during dry-run, checking exempt files, missing alternate object storage, mishandling macro order, or reporting path glob chars unsafely. Signals are exact output strings, nonzero statuses, grep counts for `nonCanonicalPointer`, `unexpectedGitObject`, `corruptObject`, `openError`, repair messages, and bad-object file existence checks.
