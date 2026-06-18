# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/file.c

Implements CIFS file open/create, share-mode compatibility, delete-on-close, stat, locking, and close logic.

Key points:
- Maintains an opportunistic/share lock table `locktab` keyed by name hash.
- `getopl` enforces SMB share compatibility:
  - `FILE_SHARE_COMPAT` special rules.
  - read/write/delete desired access vs existing share permissions.
  - canonicalizes path to existing locked path spelling when matched.
- `putopl` removes lock records when last reference closes and performs remove-on-close if requested.
- `createfile` implements SMB create/open dispositions:
  - supersede, open, create, open-if, overwrite, overwrite-if.
  - directory-only and non-directory-only checks.
  - readonly attribute effects on creation mode.
  - delete-on-close validation.
  - truncation/size setting for overwrite/new files.
  - fallback create using canonical parent/name lookup.
- Returns create action and optional `Dir` stat data.
- `statfile` stats by fd or path.
- `lockfile` provides a single logical lock owner per `Opl`.
- `deletefile` toggles delete-on-close; `deletedfile` queries it.
- `putfile` closes fd, clears lock owner, releases `Opl`, and frees the file.

Dependencies and interactions:
- Uses `xdirstat`, `splitpath`, `conspath`, `smbmkerror`, DOS/NT constants, and path hash/name comparators.
- Returned `File` objects are stored in tree fid tables.

Research relevance:
- This is core SMB filesystem semantic emulation over Plan 9 files: share modes, create dispositions, and deletion behavior.
