# sources/sync-backup/borg/src/borg/testsuite/archive_test.py

Purpose: unit-tests core archive data helpers: statistics accounting/progress output, archive timestamp parsing, cache chunk buffering, robust item unpacking/resync, msgpack item validation, backup I/O exception wrapping, UID/GID restoration selection, path sanitization, and archive lookup by ID.

Important APIs/types/functions: `stats` fixture builds a `Statistics` object. `MockCache` supplies `add_chunk` and repository async response behavior for `CacheChunkBuffer`. `make_chunks`, `_validator`, `process`, and `split` construct msgpacked item streams and exercise `RobustUnpacker`. Tests cover `Statistics.show_progress`, `Archive.ts`, `CacheChunkBuffer.flush`, `valid_msgpacked_dict`, `backup_io`, `backup_io_iter`, `get_item_uid_gid`, `Item` path validation, and `Archives.get_by_id`.

Control flow: progress tests route output through `StringIO` and a TTY-like subclass to check terminal padding/truncation versus file newline behavior and JSON progress records. Chunk-buffer tests pack `Item` instances, force full and partial flushes, then unpack cached bytes to verify order and completeness. Robust unpacking tests feed split/corrupt/missing chunks, optionally call `resync`, and assert which dicts or garbage bytes emerge. UID/GID tests walk numeric, named, forced, default, invalid, and Windows-specific branches.

State and persistence behavior: tests use in-memory mocks and msgpack buffers rather than real repositories. The only external state is OS user/group lookup for the current uid/gid and nonexistent names. `PlaintextKey`, `Manifest`, and `Archive` are constructed with mocks for timestamp parsing.

Dependencies and integration points: integrates with `borg.archive` (`Archive`, `CacheChunkBuffer`, `RobustUnpacker`, `Statistics`, `backup_io` helpers), `borg.item.Item`, `borg.manifest.Archives`, `borg.crypto.key.PlaintextKey`, Borg msgpack helpers, and platform user/group lookup.

Risks: progress string expectations are tightly coupled to formatting widths and terminal columns. User/group tests depend on the current process uid/gid resolving to names on Unix. Robust unpacker expectations deliberately expose msgpack garbage as integers before resync, so changing unpacker policy will affect tests.

Test signals: strong unit-level coverage for archive helper invariants, especially byte stream recovery and metadata coercion. It does not cover full repository persistence; CLI integration suites cover that separately.
