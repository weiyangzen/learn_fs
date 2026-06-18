## sources/sync-backup/bup/test/ext/test-install

Purpose: smoke test for install layout and installed command execution.

Important control flow: ensures the working `bup` is a symlink and `lib/cmd/bup.c` exists, unsets `GIT_DIR`, runs `dev/make PREFIX=... install`, prepends installed `bin` to PATH, checks `bup version`, optionally checks installed help if pandoc is available, and initializes an installed repo.

State and dependencies: writes an installation tree under a temp directory. Depends on make/install rules, native launcher, documentation generation, and PATH lookup.

Risks covered: install-time library discovery, launcher `PYTHONPATH` setup, installed command availability, and docs integration.
