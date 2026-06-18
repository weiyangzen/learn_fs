# File Research: sources/windows/winbtrfs/src/shellext/propsheet.h

Read status: complete, 192 lines.

This header declares the Btrfs property sheet COM class and supporting POSIX/Btrfs flag constants.

Key declarations:
- Defines POSIX permission and special mode bits if not already available.
- Defines Btrfs inode flag constants used by the property page, including nodatasum, nodatacow, readonly, nocompress, prealloc, sync, immutable, append, nodump, noatime, dirsync, and compress.
- `BtrfsPropSheet` implements `IShellExtInit` and `IShellPropSheetExt`.
- Constructor initializes COM lifetime state, edit flags, access flags, background scan state, aggregate size counters, sector size, format buffers, and display state.
- Destructor releases selection `STGMEDIUM` if owned and decrements `objs_loaded`.
- Public methods include COM methods plus UI/edit helpers used by dialog procedures.
- Public state is intentionally exposed for dialog procedures, including readonly/access state, size format buffers, scan thread handle, mode/flag masks, inode identifiers, uid/gid, compression state, and mixed-selection flags.
- Private state includes refcount, selection data, edit-change booleans, aggregate size counters, directory search queue, standalone filename, sector size, and file-loading/apply helpers.

Integration:
- Implemented in `propsheet.cpp`.
- Instantiated by `Factory::CreateInstance`.
- Registered by `main.cpp` for `Folder` and `*` property sheet handlers.
- Shares `objs_loaded` for COM unload tracking.

Risk and maintenance notes:
- Many fields are public to simplify dialog callbacks. This keeps code direct but makes invariants harder to enforce.
- Background thread handle and shared aggregate fields are exposed without synchronization primitives.
- Copying is not disabled. COM objects are heap-managed and not copied in current code.
