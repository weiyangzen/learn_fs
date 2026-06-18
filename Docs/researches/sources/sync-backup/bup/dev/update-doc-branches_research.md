# sources/sync-backup/bup/dev/update-doc-branches

## Purpose
Updates dedicated Git branches containing generated manpage and HTML documentation from current Markdown docs.

## Important APIs, Types, and Functions
Requires full refs for man/html branches, checks clean working tree, runs `dev/make`, uses temporary Git index, `git add -f`, `git write-tree --prefix=Documentation`, `git commit-tree`, and `git update-ref`.

## Control Flow
Validates args/refs, refuses uncommitted changes, builds docs, creates a temp index, stages generated files per format, creates a commit with parent `refs/heads/<fmt>`, and updates the target ref.

## State and Persistence Behavior
Mutates Git refs for documentation branches and creates temporary index files under `t/tmp`.

## Dependencies and Integration Points
Invoked by `make update-doc-branches`; depends on doc generation and Git plumbing.

## Risks and Test Signals
Risks include hard-coded parent refs, destructive ref updates, clean-tree requirement, and missing `t/tmp` vs `test/tmp` convention. Signals are updated refs pointing to commits with generated docs.
