<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tag -->
# sources/sync-backup/bup/test/ext/test-tag

Purpose: tests `bup tag` creation, deletion, validation, force deletion, and error handling. Important APIs are `bup tag`, `bup index`, `bup save`, Git `tag`, and stderr capture. Control flow saves sample data on branch `main`, verifies no initial tags, checks delete of missing tags with and without force, rejects missing target and invalid empty/dotted tag names, rejects nonexistent targets, creates `tag-1`, rejects duplicate creation, then deletes it. State is Git `refs/tags/*` in the bup repo. Dependencies are Git tag plumbing and bup VFS target resolution. Risks are tag name validation differences and accidentally leaving refs after failed commands. Test signals are exact `git tag` output and expected command failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tag -->
