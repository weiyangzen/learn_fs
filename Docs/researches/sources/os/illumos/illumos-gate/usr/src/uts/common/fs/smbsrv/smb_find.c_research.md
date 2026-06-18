# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_find.c

## Role

Implements legacy SMB1 directory search commands that use 8.3 names and resume keys: `SMB_COM_SEARCH`, `SMB_COM_FIND`, `SMB_COM_FIND_CLOSE`, and `SMB_COM_FIND_UNIQUE`.

## Major Responsibilities

- Decodes old search/find request formats, including search attributes and resume keys.
- Opens and reuses `smb_odir_t` directory search objects.
- Handles first-search and resume-search flows.
- Encodes legacy directory entries with 21-byte resume keys and 8.3 filenames.
- Supports special volume-label-only search responses.
- Caps returned entries at `SMB_MAX_SEARCH`.
- Saves directory cookies for indexed resume.
- Explicitly closes find handles for `SMB_COM_FIND_CLOSE`.
- Opens, returns, and closes a one-shot search for `SMB_COM_FIND_UNIQUE`.

## Key Functions

- `smb_com_search()` implements core search, disables long-name semantics, handles volume-label requests, manages resume keys, reads directory entries, and optionally uppercases short names for older clients.
- `smb_com_find()` implements the LANMAN find protocol with similar resume-key handling but different error behavior.
- `smb_com_find_close()` extracts the open directory id from the resume key and closes the associated `smb_odir_t`.
- `smb_com_find_unique()` performs a one-shot search and closes the directory before returning.
- `smb_name83()` converts a short filename into the 11-byte base/ext resume-key form.
- `smb_pre_*()` and `smb_post_*()` functions provide DTrace hooks for each command.

## Research Notes

These commands cannot return Unicode or long filenames. The implementation skips names needing mangling when no shortname is available, and it treats zero matches on an initial search as `NO_MORE_FILES`.
