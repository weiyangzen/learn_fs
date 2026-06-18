# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_sftp.py

## Purpose
This module is a no-network integration test suite for Tahoe-LAFS SFTP frontend behavior, centered on `allmydata.frontends.sftpd.SFTPUserHandler` and the file-handle abstractions it exposes to Twisted Conch. It validates path parsing, directory listing, metadata, reading, writing, deletion, rename semantics, OpenSSH extensions, and shell/session behavior against an in-memory Tahoe grid.

## Important APIs, Types, And Functions
`Handler` combines `GridTestMixin`, `ShouldFailMixin`, `ReallyEqualMixin`, and `unittest.TestCase`. If Twisted Conch is unavailable, the whole class is skipped. `shouldFailWithSFTPError(expected_code, which, callable, *args, **kwargs)` wraps a callable with `defer.maybeDeferred`, expects `sftp.SFTPError`, and checks the exact SFTP status code. `_set_up` creates a one-client no-network grid, a root dirnode, reloads SFTP module state, and constructs `SFTPUserHandler`. `_set_up_tree` builds the reusable fixture: mutable file, readonly view, immutable files including a non-ASCII name, LIT directories, an unknown future URI, and a self-referential loop directory with fixed metadata.

Helper comparators `_compareDirLists` and `_compareAttributes` validate Conch-style directory entries and attrs dictionaries. The tests exercise `SFTPUserHandler` methods including `gotVersion`, `_path_from_string`, `realPath`, `openDirectory`, `getAttrs`, `setAttrs`, `openFile`, `removeFile`, `removeDirectory`, `renameFile`, `makeDirectory`, `extendedRequest`, and session adapter methods from `conch_interfaces.ISession`.

## Control Flow
Most tests build a Deferred callback chain. Setup creates the grid and tree, then each operation appends either a success assertion or an expected SFTP error assertion. Read tests open handles, call `readChunk` at normal, zero-length, near-EOF, EOF, and after-EOF offsets, inspect handle and handler attrs, verify write operations are denied on read-only handles, and assert closed handles reject further operations.

Write tests cover SFTP flag combinations in depth: invalid empty paths, `TRUNC` without existing files, `EXCL` without `CREAT`, writes to directories or unknown nodes, immutable directory denial, readonly mutable caps, direct URI writes, create/truncate/append behavior, sparse writes with NUL filling, resize via `setAttrs`, write-only read denial, idempotent close, replacing immutable files, writing mutable files in place, and changing parent links to readonly. They also test read/write handles, renaming links while handles are open, and a deliberate open/rename race using a delayed Deferred.

Removal and rename tests distinguish file removal from directory removal, allow unknown link removal, preserve open read handles after unlink, prevent deleted heisenfiles from being committed on close, reject ordinary rename over existing targets, and validate OpenSSH POSIX rename replacement semantics through `extendedRequest(b"posix-rename@openssh.com", ...)`. Session tests adapt the handler to `ISession`, verify `df -P -k /`, unsupported commands, shell rejection, CRLF endings, and process termination reasons. Extended-request tests validate `statvfs@openssh.com`, unsupported requests, and malformed POSIX rename payloads.

## State And Persistence Behavior
All persistent application state is inside the no-network Tahoe grid: dirnodes, mutable file versions, readonly caps, immutable file shares, metadata, and links. The SFTP layer also maintains transient heisenfile state for open write handles, tracked through `sftpd.all_heisenfiles` and `handler._heisenfiles`; most tests assert both are empty at the end. This is a key cleanup signal because open-write placeholder state must not leak across operations or tests.

Write behavior persists only on close for some handle types, but created placeholder links may be visible earlier. Tests intentionally remove or rename open handles to validate final commit behavior. Mutable writes preserve storage identity when using writable caps, while chmod-like permission changes can diminish parent links to readonly without changing storage index. Grid destruction via `nuke_from_orbit` verifies read and close failure paths when shares disappear.

## Dependencies And Integration Points
The module integrates Twisted Deferreds, Twisted Conch SFTP constants and interfaces, Tahoe no-network grid machinery, mutable publish data, immutable upload data, `download_to_data`, `IDirectoryNode`, Tahoe-specific exceptions (`ExistingChildError`, `NoSuchChildError`, `NotWriteableError`), and process-end marker classes (`ProcessDone`, `ProcessTerminated`). It is tightly coupled to `allmydata.frontends.sftpd` internal behavior, including `_reload`, `_convert_error`, global heisenfile bookkeeping, and request-extension encodings.

## Risks And Edge Cases
The suite encodes many user-visible compatibility decisions: invalid UTF-8 maps to `FX_NO_SUCH_FILE`, ordinary rename-over-existing maps to `FX_PERMISSION_DENIED` for sshfs compatibility, unsupported links/shells map to explicit SFTP failures, and `WRITE | TRUNC` without `CREAT` is accepted for POSIX interoperability despite SFTP spec tension. It is sensitive to exact SFTP status codes, directory-list text formatting, timezone-dependent date rendering, Twisted Conch availability, and race handling around open files.

## Test Signals
Passing tests signal that the SFTP frontend can safely expose Tahoe directories as SFTP paths, including Unicode names, cap-based `uri/` access, readonly and mutable capability boundaries, LIT directory handling, unknown-node protection, correct file-handle lifecycle, cleanup of transient write state, OpenSSH extension support, and robust conversion from Tahoe/Twisted failures into SFTP error codes.
