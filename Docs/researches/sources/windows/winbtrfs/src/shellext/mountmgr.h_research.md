# File Research: sources/windows/winbtrfs/src/shellext/mountmgr.h

Read status: complete, 29 lines.

This header declares the mount manager wrapper and result type.

Key declarations:
- `mountmgr_point` stores a symbolic link, device name, and raw unique ID.
- `mountmgr` owns a mount manager handle and exposes `create_point`, `delete_points`, and `query_points`.
- `query_points` returns a `std::vector<mountmgr_point>`.

Integration:
- Implemented in `mountmgr.cpp`.
- Used by device enumeration logic in `devices.cpp`.

Risk and maintenance notes:
- The class owns a raw `HANDLE` rather than a reusable RAII handle wrapper. Copying is not explicitly disabled, so accidental copies would double-close; current code uses stack instances without copying.
