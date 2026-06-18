## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_ioctl.go

Purpose: Linux reflink copy-range backend using clone ioctls.

Important APIs/types/functions: Registers `CopyRangeMethodIoctl`; `copyRangeIoctl` performs whole-file or range clone through `unix.IoctlFileClone`/`IoctlFileCloneRange`.

Control flow: Checks source size, converts a range ending exactly at source EOF to length zero per ioctl semantics, optimizes whole-file clone when offsets and length are zero, otherwise fills `unix.FileCloneRange` and invokes ioctl.

State and persistence: Creates copy-on-write clone extents in destination file.

Dependencies and integration points: Linux build tag; uses `withFileDescriptors` and copy-range registry.

Risks: Requires filesystem reflink support. EOF and zero-length semantics must be exact to avoid cloning more than intended.

Test signals: No direct tests here; copy-range integration should validate fallback.
