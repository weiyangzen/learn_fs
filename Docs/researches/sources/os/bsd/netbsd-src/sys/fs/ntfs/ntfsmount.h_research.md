# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfsmount.h

Defines NTFS mount arguments and user-visible mount flags.

Key contents:
- `NTFS_MFLAG_CASEINS`: case-insensitive behavior.
- `NTFS_MFLAG_ALLNAMES`: expose all NTFS name variants.
- `struct ntfs_args`:
  - Device path, compatibility padding, uid, gid, mode, and mount flags.
- `NTFS_MFLAG_BITS` bit-description string.

Role:
- Installed public mount argument header used by mount tools and kernel NTFS mount code.
