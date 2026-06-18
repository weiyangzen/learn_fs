# File Research: sources/local-fs/xfsdump/common/cldmgr.h

Purpose: public interface for child-thread management.

Key declarations:
- `cldmgr_init(void)` initializes the child manager.
- `cldmgr_create(entry, streamix, descstr, arg1)` starts a child thread tied to a stream index and description.
- `cldmgr_stop(void)` requests graceful stop.
- `cldmgr_join(void)` joins exited children and returns an `EXIT_*` status.
- `cldmgr_stop_requested(void)` exposes stop polling for workers.
- `cldmgr_remainingcnt(void)` returns count of alive children.
- `cldmgr_otherstreamsremain(streamix)` checks whether other stream workers are still alive.

Interactions:
- Depends on common types such as `bool_t`, `ix_t`, and exit-code constants from surrounding includes in users.
- Used by content/drive/dialog code to coordinate worker termination and media-change interruption behavior.

Risks/notes:
- API expects cooperative children that periodically poll `cldmgr_stop_requested`.
