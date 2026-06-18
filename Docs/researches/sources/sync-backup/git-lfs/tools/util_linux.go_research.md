# sources/sync-backup/git-lfs/tools/util_linux.go

Purpose: Linux reflink/copy-on-write clone support via `FICLONE` ioctl.

Important APIs/types/functions: `CheckCloneFileSupported`, `CloneFile`, and `CloneFileByPath`.

Control flow: support probe creates temp src/dst and calls `CloneFile`. `CloneFile` succeeds only when both arguments are `*os.File`, then calls `unix.IoctlFileClone`. Path clone opens source, creates/truncates destination, and delegates.

State and persistence: creates/removes probe temp files and writes/truncates destination for path clone.

Dependencies and integration points: used by `CopyWithCallback` to avoid byte copying when filesystem supports reflinks.

Risks: filesystem support varies; ioctl errors are returned to caller, which may affect fallback behavior depending on caller path. Path clone truncates destination.

Test signals: common `TestMethodExists`; no Linux-specific success test in this subset.
