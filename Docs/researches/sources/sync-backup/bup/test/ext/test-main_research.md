<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-main -->
# sources/sync-backup/bup/test/ext/test-main

Purpose: smoke-tests top-level `bup` option parsing and environment overrides. The important surface is the `bup()` wrapper around the repository executable and invocations of `bup --bup-dir=repo init` and `bup -d repo fsck`. Control flow creates a temp directory, initializes a repository through the long option form, then verifies the short `-d` form can find and check it. State is the `repo` directory under the temp workspace; no source tree is saved. Dependencies are minimal: WvTest, the bup command dispatcher, and Git repository initialization/checking. Risks are narrow but important because global option parsing runs before subcommand dispatch; regressions here can break every command. Test signals are successful initialization, `fsck`, and cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-main -->
