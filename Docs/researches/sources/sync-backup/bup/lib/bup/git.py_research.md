<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/git.py -->
# sources/sync-backup/bup/lib/bup/git.py

## Purpose
This is bup's primary Git storage integration layer. It treats a bup repository as a Git bare repository, provides object hashing/tree encoding helpers, reads `.idx` and `.midx` pack indexes with mmap, writes new pack/index pairs, manages refs and repository initialization, and exposes a cached `git cat-file` pipe for object reads.

## Important APIs, Types, And Functions
Key public surfaces include `repo()`, `init_repo()`, `establish_default_repo()`, `git_config_get()`, `calc_hash()`, `tree_encode()`, `tree_iter()`, `find_tree_entry()`, `PackIdxV1`, `PackIdxV2`, `PackIdxList`, `LocalPackStore`, `PackWriter`, `PackIdxV2Writer`, `list_refs()`, `read_ref()`, `update_ref()`, `rev_list()`, `rev_parse()`, `CatPipe`, `catpipe()`, `walk_object()`, and `MissingObject`. Name mangling helpers (`mangle_name`, `demangle_name`) encode bup's segmented-file convention with `.bup`, `.bupl`, and `.bupm` names.

## Control Flow
Repository functions first resolve `repodir` or explicit `repo_dir`, then call Git CLI commands with `GIT_DIR` in `_gitenv()`. Index lookup flows through `PackIdxList.exists()`: optional bloom rejection, `.midx` lookup, direct `.idx` lookup, recency reordering, and offset fallback for midx hits. Pack writing flows from `PackWriter.maybe_write()` to `_encode_packobj()`, `LocalPackStore.write()`, `finish_pack()`, `.idx` creation, atomic rename into `objects/pack`, fsync, optional callback, and `auto_midx()`. `CatPipe.get()` serializes requests to a long-lived `git cat-file --batch-command` or legacy batch pair and returns an iterator that must be consumed before another request.

## State And Persistence Behavior
Global state includes `repodir`, `verbose`, `_catpipe_for`, `_git_great`, and pack-index search counters. Persistent state is Git repository data: `config`, `HEAD`, `objects/pack/pack-*.pack`, `.idx`, `.midx`, `bup.bloom`, refs, and reflogs. Temporary pack files are staged below `objects/pack-tmp-*` and renamed only after full pack checksum/index generation. Open mmaps and cat-file subprocesses are explicitly close-checked through `__del__` assertions.

## Dependencies And Integration Points
This module depends on Git CLI, zlib, mmap helpers, `_helpers.write_idx`, bloom/midx support, commit serialization, `hashsplit` modes, config parsing, and `bup.path.exe()` for invoking `bup midx`/`bup bloom`. It is the storage backend for `repo/local.py`, VFS traversal, save/get transfer code, server protocol object receipt, and tests around pack/index handling.

## Risks And Edge Cases
Resource lifecycle is important: `PackIdxList` asserts only one instance, mmaps must close, and `CatPipe` forbids overlapping reads. A partially consumed cat-file iterator can block future reads. `PackIdxList.refresh()` deletes redundant or broken midx files, so stale open maps must be closed before `auto_midx()`. Git CLI failures are converted to `GitError`, but some commands intentionally treat empty results as nonfatal. Hash/tree parsing assumes well-formed Git object data and uses assertions heavily. Repository initialization mutates global `repodir`.

## Test Signals
Relevant signals are in `test/int/test_git.py`, `test/int/test_midx.py`, `test/ext/test-cat-file`, `test/ext/test-init`, `test/ext/test-walk-object-order`, `test/ext/test-list-idx`, `test/ext/test-packsizelimit`, and repository transfer tests. Good coverage should exercise pack v1/v2 parsing, midx refresh/removal, cat-file missing objects, config parsing, ref updates, repo detection, and `walk_object()` post-order traversal.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/git.py -->
