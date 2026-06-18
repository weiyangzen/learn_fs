# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.c

## Purpose

Provides SMBFS utility routines for timestamp conversion, full path encoding, server-to-local filename conversion, and SMB credential allocation.

## Main Entry Points

Time conversion:
- `smb_time_local2server()` and `smb_time_server2local()` apply server timezone offsets to Unix seconds.
- `smb_time_NT2local()` converts NT 100ns timestamps since 1601 to Unix timespec.
- `smb_time_local2NT()` converts Unix time to NT timestamp units.
- `smb_time_unix2dos()` and `smb_dos2unixtime()` convert between Unix timespec and FAT date/time fields.

Path/name conversion:
- `smbfs_fullpath()` writes a full SMB path into an `mbchain`, with Unicode padding/termination when required, dialect-dependent uppercase conversion, existing node path, optional separator, optional child name, and NUL terminator.
- `smbfs_fname_tolocal()` converts server filenames through `vc_tolocal` iconv state and applies case options; for failed Unicode conversion, it substitutes `?` to avoid embedded NULs in local names.

Credentials:
- `smbfs_malloc_scred()` and `smbfs_free_scred()` allocate/free `struct smb_cred` using SMBFS malloc type.

## Integration Points

Used by `smbfs_smb.c`, I/O paths, and VOP code when building SMB requests and decoding server directory entries.

## Risks and Review Notes

Timestamp conversion mixes server timezone offsets for DOS/server seconds but treats NT timestamps as UTC. Filename conversion has a Unicode failure fallback that preserves operation progress at the cost of lossy names.
