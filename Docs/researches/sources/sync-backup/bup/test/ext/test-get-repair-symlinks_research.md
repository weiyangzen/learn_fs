## sources/sync-backup/bup/test/ext/test-get-repair-symlinks

Purpose: tests repair behavior for missing and mismatched symlink blobs.

Important control flow: first saves a symlink with metadata, drops its blob, verifies ordinary get notices the missing object, and checks `--rewrite` and `--repair` restore the link blob with trailers. It then rewrites the symlink blob to a mismatched target, verifies `--rewrite` rejects and `--repair` fixes it. Finally it creates a bare Git-style repo without Bup metadata, drops the symlink blob, and verifies only `--repair` replaces it with an explanatory blob.

State and dependencies: direct object deletion and Git tree edits. Depends on VFS symlink target rules, `rewrite._rewrite_link()`, `bup join`, and commit trailer checks.

Risks covered: Bup must prefer metadata symlink targets when present, detect inconsistent blob targets, and distinguish restorable metadata-backed links from unrecoverable old/git symlinks.
