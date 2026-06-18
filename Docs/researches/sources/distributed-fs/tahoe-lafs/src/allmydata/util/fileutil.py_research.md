# sources/distributed-fs/tahoe-lafs/src/allmydata/util/fileutil.py

## Purpose

This module provides Tahoe-LAFS filesystem primitives: retrying Windows file removal/rename, temporary files, encrypted temporary storage, recursive directory operations, atomic-ish writes, path normalization, Windows long path support, disk-space stats, no-overwrite replacement, and path metadata snapshots.

## APIs and control flow

`rename()` and `remove()` retry with exponential sleeps for transient Windows sharing failures. `ReopenableNamedTemporaryFile` creates a named placeholder and deletes it on shutdown. `EncryptedTemporaryFile` encrypts file contents at rest with AES counter-like offset handling. Directory helpers include `make_dirs_with_absolute_mode()`, `make_dirs()`, `rm_dir()`, `du()`, and `remove_if_possible()`. File helpers include `move_into_place()`, `write_atomically()`, `write()`, `read()`, and `put_file()`.

Path helpers enforce absolute unicode paths, expand `~`, construct Windows `\\?\` long paths, read Windows environment variables through ctypes, and collect disk stats using `GetDiskFreeSpaceExW` or `statvfs`. Replacement helpers differ by platform: Windows uses `ReplaceFileW`, POSIX uses hard-link no-overwrite or rename replacement. `get_pathinfo()` returns a `PathInfo` tuple from `lstat`.

## State, dependencies, risks, and tests

State is filesystem state and temporary AES keys. Dependencies include platform APIs, Twisted logging, Tahoe AES, `six.reraise`, and local assertions. Integration spans config writes, storage accounting, upload/download tempfiles, pid cleanup, and node path handling.

Risks are high: atomicity differs on Windows, recursive deletion is manually implemented, encrypted tempfiles require seek between read/write direction changes, long-path normalization is subtle, disk stats can fail or return quota-sensitive values, and assertion-based absolute-path preconditions protect destructive operations. Test signals should cover Windows and POSIX replacement semantics, temp cleanup, encrypted read/write/seek/truncate, recursive removal races, disk-space reserved values, unicode/long paths, symlink pathinfo, and write atomicity under existing targets.
