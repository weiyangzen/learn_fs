# sources/sync-backup/rsync/mkgitver

## Purpose
`mkgitver` generates or refreshes `git-version.h` with an `RSYNC_GITVER` macro based on `git describe`, but only when the current repository description looks like an rsync 3.x version tag.

## Important APIs, Types, and Functions
This is a shell script with no functions. It uses `dirname`, `touch`, `git describe --abbrev=8`, `sed`, `diff`, `mv`, and `rm`.

## Control Flow
The script ensures `git-version.h` exists. If the source directory is a git worktree or gitfile, it runs `git describe --abbrev=8`, appends a dash, and filters the result through a sed expression matching `v3.<num>.<num>` with optional `pre<num>` and a following dash. On a valid description, it writes a temporary header defining `RSYNC_GITVER`, compares it to the existing header, and atomically replaces the header only when the content changed.

## State and Persistence
Persistent state is the generated `git-version.h` file. A temporary `git-version.h.new` is removed when unchanged or moved into place when updated.

## Dependencies and Integration Points
The script is used by the build process to embed a git-derived version string. It depends on being run from a build directory where `git-version.h` should be written, while using the script directory to decide whether git metadata exists.

## Risks
The sed pattern is intentionally narrow and ignores non-3.x tags or unusual descriptions. If run outside a git checkout, it leaves the header as-is after touching it. The script does not quote `$srcdir` in all places, so paths containing spaces would be fragile.

## Test Signals
Tests should cover non-git source archives, valid `v3.2.7-...` descriptions, pre-release descriptions, invalid tag names, unchanged header no-op behavior, changed header replacement, and build-directory invocation separate from source directory.
