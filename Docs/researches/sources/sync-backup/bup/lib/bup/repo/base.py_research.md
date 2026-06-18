<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/base.py -->
# sources/sync-backup/bup/lib/bup/repo/base.py

## Purpose
This module defines shared repository configuration derivation and the abstract protocol expected of local and remote repository backends.

## Important APIs, Types, And Functions
Important pieces are `_make_base()` and `RepoProtocol`. `_make_base()` returns a frozen dataclass with compression level, max pack size, and max pack objects. `RepoProtocol` lists methods for reading, resolving, writing, refs, indexes, config, and object existence.

## Control Flow
`_make_base()` consults repository config for `pack.compression`, then `core.compression`, then `pack.packSizeLimit` when explicit values are absent. `RepoProtocol` methods are decorated with `helpers.notimplemented`, making accidental use of the base class fail clearly with the class and method name.

## State And Persistence Behavior
There is no persistent state. The generated base config object is immutable and stored by concrete repos such as `LocalRepo`.

## Dependencies And Integration Points
It depends on `compat.dataclass` and `helpers.notimplemented`. `repo/local.py` and remote repository implementations use the protocol to present a common interface to VFS, protocol server, save, get, and ls code.

## Risks And Edge Cases
This is an informal protocol rather than a strict typing interface, so compatibility depends on concrete classes matching semantics, especially iterator consumption requirements for `cat()` and write lifecycle for `finish_writing()`/`abort_writing()`. Config key spelling must match Git config access (`pack.packSizeLimit`).

## Test Signals
Repository behavior is tested through `test/int/test_repo.py`, VFS tests, protocol tests, local/remote command integration, and save/get flows that exercise the shared interface.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/base.py -->
