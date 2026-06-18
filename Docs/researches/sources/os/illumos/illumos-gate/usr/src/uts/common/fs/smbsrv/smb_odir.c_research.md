# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_odir.c

## Summary
Implements SMB open-directory search handles (`smb_odir_t`). It manages directory-search lifetime, VOP readdir buffering, wildcard/name matching, file-info lookup, named-stream enumeration, access-based enumeration, short-name/case-conflict behavior, and resume cookies.

## Main Responsibilities
- Opens directory searches by path, by existing directory handle, or on xattr stream directories.
- Maintains the OPEN/IN_USE/CLOSING/CLOSED odir state machine.
- Reads directory entries through `smb_vop_readdir()`.
- Converts `dirent64_t` or `edirent_t` records into `smb_odirent_t`.
- Returns basic directory entries, full `smb_fileinfo_t`, or named stream info.
- Saves and restores search cookies, last filename, and resume offsets.
- Applies wildcard matching, DOS reserved-name filtering, short-name matching, CATIA conversion, ABE, and search-attribute checks.
- Follows symlinks for attribute reporting where policy permits.

## Key APIs
- `smb_odir_openpath()`, `smb_odir_openfh()`, `smb_odir_openat()`.
- `smb_odir_hold()`, `smb_odir_release()`, `smb_odir_close()`.
- `smb_odir_read()`, `smb_odir_read_fileinfo()`, `smb_odir_read_streaminfo()`.
- `smb_odir_save_cookie()`, `smb_odir_save_fname()`, `smb_odir_resume_at()`.
- `smb_odir_reopen()`.

## Important Behavior
`sm b_odir_openpath()` reduces a client path to parent directory plus pattern, checks directory type and list access, allocates an odir id, and creates the search object. `openfh` uses an already opened directory handle. `openat` opens the xattr directory of an unnamed node and searches stream-prefixed entries.

Wildcard searches repeatedly read entries until a valid UTF-8 name matches the pattern and attributes. Single-name searches perform a direct lookup once, then force EOF.

`sm b_odir_next_odirent()` refills an internal fixed buffer when needed, requests extended dirent flags when supported, optionally requests filesystem ABE, and stops when offsets reach `SMB_MAXDIRSIZE`.

For file info, symlinks are followed to report target attributes unless directory symlinks are disabled. Case conflicts can cause generated 8.3 short names to be returned in place of long names.

## State and Synchronization
The odir is listed on the tree odir list and protected by `d_mutex`. Lookups can hold OPEN or IN_USE odirs; close transitions to CLOSING; final release posts deferred deletion so tree-list iteration is not modified in place.

## Dependencies
Depends on tree/session/user references, SMB pathname reduction, VOP readdir/lookup/traverse/access, SMB wildcard and mangling helpers, CATIA translation, xattr directories, stream name policy, and access-based enumeration feature flags.

## Risks
Filename resume handling appears inverted: the `SMB_ODIR_RESUME_FNAME` branch uses the saved last cookie when `strcmp(resume->or_fname, od->d_last_name)` is nonzero, even though the comment says to use it when the names match.

ABE performed in VOP readdir is disabled by default because it can stall large directories; manual per-entry ABE is safer but more expensive.

The source documents resume-by-filename as not fully supported; callers fall back to cookie or current offset behavior.
