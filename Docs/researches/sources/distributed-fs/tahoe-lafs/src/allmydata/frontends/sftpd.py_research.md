# sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/sftpd.py

## Purpose

This module implements Tahoe-LAFS's SFTP frontend using Twisted Conch. It maps SFTP file, directory, attribute, rename, remove, and extension requests onto Tahoe capability nodes and directory operations while handling Tahoe's immutable/mutable semantics and asynchronous uploads/downloads.

## Important APIs, Types, And Functions

Helper functions include `createSFTPError()`, `eventually_callback()`, `eventually_errback()`, `_utf8()`, `_to_sftp_time()`, `_convert_error()`, `_repr_flags()`, `_lsLine()`, `_no_write()`, `_populate_attrs()`, `_attrs_to_metadata()`, and `_direntry_for()`. `OverwriteableFileConsumer` buffers downloads and overwrites in an encrypted temp file. `ShortReadOnlySFTPFile` serves small immutable read-only files from memory. `GeneralSFTPFile` handles read/write/create/truncate/append lifecycle, delayed commits, mutable overwrite, and immutable upload+link. `SFTPUserHandler` implements `ISFTPServer` and owns request handling plus per-user and global heisenfile tracking. `FakeTransport`, `ShellSession`, `Dispatcher`, and `SFTPServer` wire SSH/SFTP service behavior.

## Control Flow

On service startup, `SFTPServer` builds a Twisted portal with `AccountFileChecker`, loads SSH host keys, creates an SSH factory, and listens on the configured strports endpoint. Successful authentication returns an `SFTPUserHandler` rooted at the user's configured cap. Path parsing handles normal paths and `/uri/CAP` roots. `openFile()` validates flags, creates early write handles for race-prone clients, resolves parent/child or cap roots, performs permission checks, and returns a file handle. Reads and writes are serialized through Deferred chains. Closing a changed write handle waits for pending work, then overwrites mutable files or uploads immutable content and links it into the parent. Rename/remove/getAttrs/setAttrs coordinate with open write handles called "heisenfiles" to avoid commits landing at stale paths.

## State And Persistence

Persistent state is Tahoe grid data reached through root caps, mutable file publishes, immutable uploads, directory metadata, account files, and SSH host key files. Runtime state includes Conch session objects, open file handles, encrypted temporary files, per-user `_heisenfiles`, process-global `all_heisenfiles`, download milestone queues, overwrite heaps, Deferred chains, and convergence secret references. `_reload()` clears global heisenfile state for tests.

## Dependencies And Integration Points

The module depends on Twisted Conch SFTP/SSH interfaces, portal auth, strports, Deferreds, Foolscap eventual scheduling, Tahoe file/directory interfaces, mutable/immutable upload handles, directory metadata helpers, encrypted temporary files, frontend auth, and Tahoe logging. It is instantiated by `_Client.init_sftp_server()` when `[sftpd] enabled` is true.

## Risks

This is high-concurrency adapter code with subtle ordering constraints. Write success can be delayed until close, and close behavior differs for abandoned files. Global `all_heisenfiles` is single-process state and comments assume single-threaded updates. Rename uses `move_child_to()` with a FIXME about avoiding data loss for path moves. `setAttrs()` does not support size changes except on open handles. SFTP permissions are approximations over Tahoe caps and metadata, not POSIX ACLs. `statvfs` returns synthetic fixed values. The service requires an account file; anonymous operation is rejected. Host key file errors fail startup.

## Test Signals

Use SFTP integration tests for login, path normalization, `/uri` access, invalid UTF-8 paths, reads of small immutable and large/mutable files, write/create/truncate/append/close flows, delayed write errors, close after disconnect, rename and remove with open write handles, metadata/no-write propagation, directory listing longnames, unsupported symlink requests, OpenSSH `posix-rename` and `statvfs` extensions, host key loading, and account-file authentication failures.
