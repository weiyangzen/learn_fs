# sources/sync-backup/kopia/cli/command_content_rewrite.go

## Purpose
Content rewrite command that rewrites selected content into new packs, supporting deleted-content inclusion and progress output for repository repair/compaction workflows.

## APIs, Types, and Functions
Important APIs include types `commandContentRewrite`; functions/methods `setup`, `runContentRewriteCommand`, `toContentIDs`; Kingpin command(s) rewrite: Rewrite content using most recent format; flags parallelism: Number of parallel workers, short: Rewrite contents from short packs, format-version: Rewrite contents using the provided format version, pack-prefix: Only rewrite contents from pack blobs with a given prefix, dry-run: Do not actually rewrite, only print what would happen; arguments contentID: Identifiers of contents to rewrite.

## Control Flow, State, and Persistence
Control flow registers command(s) rewrite: Rewrite content using most recent format, binds flags parallelism: Number of parallel workers, short: Rewrite contents from short packs, format-version: Rewrite contents using the provided format version, pack-prefix: Only rewrite contents from pack blobs with a given prefix, dry-run: Do not actually rewrite, only print what would happen, accepts arguments contentID: Identifiers of contents to rewrite, then runs through a direct repository write action. The implementation rewrites selected content. State and persistence: touches content indexes, pack blobs, and content metadata, maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob, kopia/repo/content, kopia/repo/maintenance plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
