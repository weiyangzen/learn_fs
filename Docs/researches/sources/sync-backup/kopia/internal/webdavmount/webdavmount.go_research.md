<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/webdavmount/webdavmount.go -->
# sources/sync-backup/kopia/internal/webdavmount/webdavmount.go

- Purpose: Adapts Kopia snapshot filesystem entries to a read-only WebDAV filesystem.
- Important APIs/types/functions: `webdavFile`, `webdavDir`, `webdavFileInfo`, `webdavFS`, `OpenFile`, `Stat`, `findEntry`, `removeEmpty`, `WebDAVFS`.
- Control flow: `OpenFile` resolves a slash path through `findEntry`, opens directories with iterators and files with lazy readers, rejects write/mkdir/remove/rename operations, skips symlinks in directory reads, and wraps entries as `os.FileInfo`.
- State and persistence: Keeps lazy file reader state under a mutex and directory iterator state; no writes are allowed.
- Dependencies and integration points: Integrates `fs`, `x/net/webdav`, and Kopia logging; used by mount/server paths.
- Risks and edge cases: Symlinks are skipped with a one-time global log; read-only errors must match WebDAV client expectations.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/webdavmount/webdavmount.go -->
