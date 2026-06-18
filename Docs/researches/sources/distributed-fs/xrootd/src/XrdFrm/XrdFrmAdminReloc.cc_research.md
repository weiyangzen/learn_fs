<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminReloc.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminReloc.cc

## Purpose
`XrdFrmAdminReloc.cc` contains a private implementation for relocating a file between cache spaces by allocating a target placeholder, copying data, preserving metadata, renaming into place, adjusting space accounting, and cleaning up source remnants.

## Important Functions
`Reloc(char *srcLfn, char *Space)` parses the target space, maps source and temporary target LFNs/PFNs, validates that source and target spaces differ, creates a target file via `ossFS->Create()`, copies bytes with `RelocCP()`, applies timestamps, renames target to source LFN, updates `XrdOssSpace`, and handles symlinked source remnants. `RelocCP()` first tries mmap plus segment writes, then falls back to traditional `pread()`/`pwrite()` copying. `RelocWR()` performs EINTR-safe positional writes.

## Control Flow, State, And Persistence
The operation is heavily persistent: it creates a `.anew` placeholder, copies file contents, updates mtime, renames through OSS, adjusts usage buckets, and may create or remove symlinks. A local RAII `relocRecover` object tries to unlink the target on early return. Copying proceeds in 1 MiB segments.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig`, OSS create/rename/unlink, `XrdOssSpace`, `XrdOssPath`, `XrdOucEnv`, POSIX mmap/pread/pwrite/utime, and admin parsing helpers. Notably, current `CMakeLists.txt` does not list this file in the `frm_admin` executable, and public `XrdFrmAdmin::Reloc()` in `XrdFrmAdmin.cc` delegates directly to `Config.ossFS->Reloc()`, so this implementation may be stale or unlinked.

## Risks And Test Signals
There is a likely precedence bug: `srcLsz = readlink(...) < 0` assigns a boolean rather than the link length. The lock-file timestamp branch sets a new lock path and returns `0`, apparently aborting before rename whenever a lock file exists. `relocRecover` stores `trgPfn` in a field named `Lfn` and calls `ossFS->Unlink()` without explicit PFN flags. Tests should first confirm whether this file is linked; if revived, cover symlink sources, existing lock files, copy fallback after mmap failure, partial write/read failures, usage adjustment rollback, and cleanup of `.anew` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminReloc.cc -->
