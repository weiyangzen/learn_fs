# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.c

## Purpose
Implements the 9P request handlers for `dossrv`, translating Plan 9 file operations into FAT directory and file mutations.

## Key Behavior
- Handles `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- `rattach()` creates/cleans a root fid, opens or references an `Xfs`, parses the FAT format with `dosfs()`, and initializes a synthetic root qid.
- `rwalk()` clones when needed, supports `.`, `..` via `walkup()`, normalizes names, searches directories including long names, and maps DOS directory attributes to qid type bits.
- `ropen()` enforces open-mode permissions, read-only DOS attributes, ORCLOSE parent checks, and truncation requests.
- `rcreate()` validates parent directory writability, classifies/generates 8.3 aliases for long names, allocates an initial cluster for directories, writes DOS entries, and creates `.`/`..` records.
- `rread()` delegates to `readdir()` or `readfile()` after checking read-open state.
- `rwrite()` delegates to `writefile()` after checking write-open state.
- `rremove()` rejects root, read-only, or non-empty-directory removal, truncates file clusters, marks short and preceding long-name entries deleted, updates parent time, and syncs.
- `rstat()` converts a DOS entry and any preceding long filename slots into a Plan 9 `Dir`.
- `rwstat()` supports truncate, mtime/mode changes, DSYSTEM/contiguous mapping through `DMEXCL`/`DMAPPEND`, and rename through delete/recreate of directory entries.
- Renames preserve invisible creation/access fields and relocate other fids that pointed to the old directory slot.

## Interfaces And Dependencies
- Uses global 9P request/reply buffers from `xfssrv.c`.
- Depends heavily on helper functions in `dossubs.c`, xfile management in `xfile.c`, and sector cache functions from `iotrack.c`.

## Notes
The server maps DOS system files to Plan 9 `DMEXCL`, and contiguous system files to `DMAPPEND`. Write and rename paths are careful to release/reacquire directory sectors to avoid lock loops.
