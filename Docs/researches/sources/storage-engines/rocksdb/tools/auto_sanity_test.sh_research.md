# sources/storage-engines/rocksdb/tools/auto_sanity_test.sh

## Purpose

This script performs forward/backward RocksDB format compatibility checks between two git commits using `db_sanity_test`.

## Important APIs, Types, and Functions

It accepts `[new_commit] [old_commit]`, defaults to the newest and tenth newest commits, uses `TMPDIR`/`/tmp` for `rocksdb-sanity-test`, and defines `makestuff` to run `make clean` and `make db_sanity_test -j32`.

## Control Flow

The script checks out the new commit, builds `db_sanity_test`, creates a DB, stores tool sources in the temp DB directory, checks out the old commit, restores the tool sources, builds again, creates an old DB, then verifies the old DB with the new binary and the new DB with the old binary. It cleans binaries and temp DBs on success.

## State and Persistence Behavior

It mutates the git working tree via `git checkout`, runs builds, creates temp DB directories, and temporarily renames built binaries. It does not restore the original branch/commit.

## Dependencies and Integration Points

It depends on git history, Makefile targets, `db_sanity_test`, and RocksDB compatibility semantics.

## Risks and Test Signals

Risks are destructive checkout/build side effects, dirty worktree hazards, unquoted paths, and no trap cleanup. Signals are successful create/verify steps and explicit exit code `2` on compatibility failure.
