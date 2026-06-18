# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.c

## Purpose
Interactive tool for building an NTFS-3G `UserMapping` file by scanning NTFS security descriptors, identifying Windows owner/group SIDs, and asking the operator which Linux UID/GID should map to those SIDs.

## Major Data Structures
- `struct USERMAPPING`: linked-list entry storing UID string, GID string, SID string, raw SID bytes, optional Windows login name, and whether the mapping is defined.
- `struct CALLBACK`: directory traversal context carrying account name, directory path, recursion depth, and scan state.
- `enum STATES`: scan mode for locating user-home roots (`STATE_USERS`), scanning account home directories (`STATE_HOMES`), or normal recursive scanning (`STATE_BASE`).

## Main Flow
- `main()` detects silent mode with `isatty(1)`.
- Non-Windows path:
  - `checkoptions()` requires at least one device and enforces `getuid() == 0`.
  - `process()` opens each NTFS device read-only through `ntfs_initialize_file_security()`.
  - It scans `/` two levels deep, first looking for `Documents and Settings` or `Users`, then other directories.
  - It closes each volume with `ntfs_leave_file_security()`.
  - `sanitize()` ensures at least one user mapping and tries to add a standard group mapping if no group was selected.
  - `outputmap()` writes `UserMapping` in the current working directory and prints instructions to move it to `.NTFS-3G`.
- Windows path:
  - Allows drive-letter arguments.
  - Can emit a minimal mapping proposal in silent stdout mode using the current Windows account SID.
  - Attempts to write directly into the target volume’s `.NTFS-3G\UserMapping`.

## NTFS/Security Behavior
- Uses `ntfs_get_file_security()` for owner, group, and DACL data.
- Owner and group SIDs are expected at offset `20` in the returned relative security descriptor buffer.
- `listaclusers()` also enumerates DACL ACE SIDs for possible group mappings.
- `domapping()` only considers SIDs with identifier authority `5` and first subauthority `21`, matching Windows domain/machine account SIDs.
- `isgenericgroup()` detects the common domain users group pattern `S-1-5-21-...-513`.
- `makegroupsid()` derives a generic group SID from a user SID by replacing the last subauthority with `513`.

## Directory Traversal
- `ntfs_read_directory()` drives `callback()`.
- Names are converted from NTFS UTF-16-ish data to UTF-8 by local helper functions `to_utf8()` and `utf8_size()`.
- Skips `"."`, `".."`, names beginning with `$`, and entries with type `2`, commented as DOS names.
- Special handling:
  - At root, looks for `Documents and Settings` and `Users`.
  - Under those directories, treats child names as Windows login names and scans them with that account context.
  - Elsewhere, scans files generically and uses ACLs to discover SIDs.

## Output Format
- Starts with a banner comment identifying platform and `USERMAPVERSION`.
- Writes records as `uid:gid:sid`.
- Emits owner-only or group-only records before records containing both UID and GID, to reduce ambiguity when a SID is used for both user and group mapping.
- Prints undecided SIDs after writing.

## Safety/Limitations
- Explicitly rejects mapping to Linux root or UID `0`.
- Requires unmounted devices on non-Windows systems.
- Uses fixed maximum buffers for security descriptors and SID/name handling (`MAXATTRSZ`, `MAXSIDSZ`, `MAXNAMESZ`).
- The local UTF-16 to UTF-8 conversion is deliberately minimal and does not handle surrogate pairs.
- `outputmap()` only treats a zero-byte `write()` as an error; short writes and `-1` writes are not robustly handled.
- Raw SID string allocation and mapping allocations are mostly retained until process exit, which is acceptable for a short-lived utility.
