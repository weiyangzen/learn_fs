<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_import.go -->
# sources/sync-backup/git-lfs/commands/command_migrate_import.go

Purpose: implements `git lfs migrate import`, rewriting history to replace matching Git blobs with LFS pointers, and a `--no-rewrite` mode that appends a new commit converting specified files.

Important APIs/types/functions: `migrateImportCommand`, `generateMigrateCommitMessage`, `checkoutNonBare`, `trackedFromFilter`, `trackedFromAttrs`, `trackedToBlob`, `rewriteTree`, and `findEntry`. It uses `clean`, `githistory.RewriteOptions`, `gitattr.Tree`, `gitobj`, and `humanize.ParseBytes`.

Control flow: ensures clean working copy, opens DB, installs hooks, then branches for `--no-rewrite`: validate args and attributes, load current commit tree, recursively replace specified blobs with cleaned pointer blobs, write a new commit with author/committer metadata, update the current ref, and checkout. Normal rewrite validates `--fixup`/`--above` flag combinations, builds a rewriter, cleans matching blobs into pointers, records attribute patterns from includes/excludes or file extensions, optionally consults per-tree attributes for fixup, updates root `.gitattributes` unless fixup, rewrites refs, and checks out.

State and persistence behavior: writes media files to `.git/lfs/objects`, writes new Git blobs/trees/commits, updates refs, mutates working tree on checkout, and caches `.gitattributes` parsing by blob SHA in `attrsCache`.

Dependencies/integration points: integrates clean filter semantics, object database writes, Git attributes parser, tasklog, migrate shared ref handling, current author/committer config, and LFS hook installation.

Risks and test signals: risks include destructive rewrite, global `attrsCache` lifetime, extension-derived tracking patterns that may overmatch, `--above` excluding equal-size blobs due to `< above`, recursive path rewrite assumptions, and symlink `.gitattributes` rejection. Test signals include include/exclude rewrite, no-rewrite single and nested paths, custom message, fixup using attributes, above threshold, extension pattern generation, checkout in bare repo skipped, and object map output.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate_import.go -->
