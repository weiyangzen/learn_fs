# File Research: sources/windows/winfsp/src/dll/fsop.c

Main filesystem operation adapter from WinFsp kernel transactions to user-supplied `FSP_FILE_SYSTEM_INTERFACE` callbacks.

Key responsibilities:
- Implements operation guard entry/leave behavior with fine or coarse SRW locking.
- Performs access checks for create, open, overwrite, target-directory open, and rename replacement cases.
- Implements Windows create dispositions: create, open, open-if, overwrite, overwrite-if, supersede, and open-target-directory.
- Creates and returns security descriptors for newly created/opened objects when requested.
- Marshals callbacks for overwrite, cleanup, close, read, write, flush, file info, set info, EA, volume info, directory query, FSCTL reparse operations, device control, security, and stream information.
- Handles named stream/reparse not-found and collision follow-up checks.
- Packs directory, stream, EA, and notify entries into WinFsp response buffers.
- Resolves reparse points and symlink chains for user-mode filesystems.
- Checks whether reparse data can be replaced safely.

Important behavior:
- File contexts can be mapped as `UserContext`, `UserContext2`, or full context depending on volume parameters.
- Fine-grained operation guarding takes exclusive locks for mutating namespace/volume operations and shared locks for selected lookup/query operations.
- Create/open paths combine WinFsp access-check helpers with filesystem callbacks and set NT create information such as `FILE_CREATED`, `FILE_OPENED`, `FILE_OVERWRITTEN`, or `FILE_SUPERSEDED`.
- `CreateEx`/`OverwriteEx` are preferred when present, with older callback forms used as fallback.
- `SetInformation` supports basic info, allocation size, EOF, disposition/disposition-ex, rename/rename-ex.
- Directory query can optimize exact-name pattern requests through `GetDirInfoByName`.
- Reparse resolution follows symlinks, handles `.` and `..`, caps attempts at 32, and returns either synthetic symlink reparse data or underlying non-symlink reparse data.
- `FspFileSystemStopServiceIfNecessary` stops the service loop on abnormal dispatcher stop.

Dependencies:
- Includes `dll/library.h`.
- Depends heavily on access/security helpers, WinFsp FSCTL transaction structures, path helpers, reparse structures, and the callback table in `FSP_FILE_SYSTEM_INTERFACE`.

Notable risks:
- This file encodes subtle Windows filesystem semantics; regressions here can affect create/open security, delete-on-close, rename replacement, reparse handling, and async I/O behavior.
- Several paths construct temporary/fake requests for access checks, so size and buffer layout correctness is important.
- Buffer packing uses 16-bit size fields and fixed maximum response sizes.
