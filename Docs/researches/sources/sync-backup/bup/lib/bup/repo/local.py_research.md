<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/local.py -->
# sources/sync-backup/bup/lib/bup/repo/local.py

## Purpose
This module implements the local repository backend for `RepoProtocol`, adapting `git.py` pack/ref/config/object helpers and `vfs` operations into the common repo interface.

## Important APIs, Types, And Functions
The central type is `LocalRepo`. Important methods include `create()`, `config_get()`, `list_indexes()`, `read_ref()`, `update_ref()`, `cat()`, `join()`, `resolve()`, `refs()`, `send_index()`, `rev_list_raw()`, `write_commit()`, `write_tree()`, `write_data()`, `just_write()`, `exists()`, `finish_writing()`, and `abort_writing()`.

## Control Flow
Construction resolves the repo path, builds base pack settings from config, creates a cached `CatPipe`, binds `rev_list`, and determines deduplication/run-midx behavior based on server mode, explicit `allow_duplicates`, `run_midx`, `bup.server.deduplicate-writes`, and `bup-dumb-server`. Writes lazily create a `PackWriter` over a `LocalPackStore`. Ref updates first finish pending writes. `send_index()` opens a requested idx and streams its mmap. `rev_list_raw()` runs Git and yields stdout chunks.

## State And Persistence Behavior
Instance state includes `repo_dir`, `_base`, `_packwriter`, `_cp`, `run_midx`, `_deduplicate_writes`, and close status. Persistent mutations are delegated to `git.init_repo()`, pack writer close/abort, and `git.update_ref()`. `close()` finishes pending writes, while `abort_writing()` aborts and removes tentative pack data.

## Dependencies And Integration Points
It depends on `git`, `vfs`, `LocalPackStore`, `PackWriter`, config errors, and process cleanup. It is the local backend used by `repo.__init__`, protocol server, VFS, save/get/ls commands, and tests.

## Risks And Edge Cases
Server deduplication config can conflict with constructor `allow_duplicates` and raises `ValueError`. Presence of `bup-dumb-server` forces deduplication off unless config disagrees, which raises `ConfigError`. `cat()` uses a shared `CatPipe`, so callers must consume data iterators before other repo operations. `abort_writing()` does not set `_packwriter` to `None` after abort, so callers should avoid reuse patterns that assume it does.

## Test Signals
`test/int/test_repo.py`, `test/int/test_vfs.py`, `test/int/test_git.py`, protocol tests, `test/ext/test-ls-remote`, `test/ext/test-on`, save/get tests, and pack-size/compression tests exercise local repo creation, config, object writing, refs, cat/join, VFS resolution, and server behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/local.py -->
