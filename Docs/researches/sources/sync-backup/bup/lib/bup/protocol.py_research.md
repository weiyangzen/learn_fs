<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/protocol.py -->
# sources/sync-backup/bup/lib/bup/protocol.py

## Purpose
This module defines bup's client/server wire protocol helpers and server command dispatcher for remote repository operations. It serializes VFS items, resolutions, IOErrors, refs, indexes, object batches, config values, and repository reads/writes over a `BaseConn`-style stream.

## Important APIs, Types, And Functions
Important helpers include `read_item()`, `write_item()`, `write_resolution()`, `read_resolution()`, `write_ioerror()`, `read_ioerror()`, `_command`, `CommandDenied`, and `Server`. Server commands include `help`, `init-dir`, `set-dir`, `list-indexes`, `send-index`, `receive-objects-v2`, `read-ref`, `update-ref`, `join`/`cat`, `cat-batch`, `refs`, `rev-list`, `resolve`, and `config-get`.

## Control Flow
Serialization tags item class names and a `has_meta` flag, then writes either `Metadata` records or integer modes. `Server.handle()` reads command lines, validates against enabled commands, maps hyphenated command names to methods, and invokes decorated handlers. `receive_objects_v2()` loops length-prefixed objects, handles zero length as finish, `0xffffffff` as suspend, optionally suggests existing indexes for deduplication, writes raw object bytes to the repo packwriter store, and validates CRCs.

## State And Persistence Behavior
`Server` tracks the connection, backend factory, active repo, suspended write state, deduplication mode, command allowlist, and vet callbacks. Persistence is delegated to the backend repo: init creates repos, receive writes pack files, update-ref mutates refs. Suspended sessions finish writing on context exit.

## Dependencies And Integration Points
It depends on `git`, `vfs`, `vint`, `Metadata`, `helpers` connection utilities, and repo backends. It is used by remote clients/servers (`repo.remote`, `client`) and bridges local storage operations to remote command calls.

## Risks And Edge Cases
The protocol is line-oriented and comments acknowledge it is not future-proof. A malformed or unauthorized command aborts handling. `receive_objects_v2()` reaches into repo internals (`_packwriter` and store), which couples it to `LocalRepo`. `cat_batch()` reads all requested refs before responding to avoid deadlock. `read_resolution()` uses `ord(port.read(1))`; unexpected EOF as empty bytes can raise before the explicit EOF check. Config exposure is allowlisted.

## Test Signals
`test/int/test_protocol.py`, remote repository tests, `test/ext/test-on`, `test/ext/test-ls-remote`, get/save remote flows, and server command tests should cover item roundtrips, resolution/error serialization, object receipt, suspended writes, ref updates, and config-get allowlisting.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/protocol.py -->
