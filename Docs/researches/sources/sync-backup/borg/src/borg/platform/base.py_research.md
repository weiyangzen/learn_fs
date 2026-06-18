# sources/sync-backup/borg/src/borg/platform/base.py

Purpose: provides fallback platform APIs plus durable file writing and atomic replacement helpers.

Important APIs/types: fallback xattr/ACL/flags functions, `sync_dir`, `safe_fadvise`, `SyncFile`, `SaveFile`, `swidth`, `getfqdn`, and `get_process_id`. `fdatasync` falls back to `fsync`; `ENOATTR` falls back to `ENODATA`.

Control flow/state: `SyncFile` creates new files exclusively, flushes/fdatasyncs, applies DONTNEED fadvise, closes, and syncs the parent directory. `SaveFile` writes to a temp file in the target directory and atomically `os.replace`s on success, deleting temp files on errors. Host identity is computed once, with `BORG_HOST_ID` override.

Dependencies/integration: used by repository side files, segment writes, security database writes, and locking identity. `platform.__init__` composes OS-specific modules with these helpers.

Risks: durability depends on OS/filesystem/hardware. `SaveFile` is last-writer-wins under concurrent writers. Base xattr/ACL stubs omit unsupported metadata. FQDN calculation can touch DNS at import.

Test signals: atomic replacement, cleanup on exception, binary/text modes, directory fsync `EINVAL` handling, no-op xattr/ACL semantics, CJK string widths, and `BORG_HOST_ID`.
