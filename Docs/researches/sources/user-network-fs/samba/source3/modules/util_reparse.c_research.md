<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.c -->
# sources/user-network-fs/samba/source3/modules/util_reparse.c

## Purpose
This utility implements SMB FSCTL reparse-point get, tag, set, and delete operations for Samba file handles. It bridges Windows reparse buffer semantics with Samba xattrs, DOS attributes, Unix special files, and symlink reparse helpers.

## Important APIs, Types, And Functions
Exported functions are `fsctl_get_reparse_point`, `fsctl_get_reparse_tag`, `fsctl_set_reparse_point`, and `fsctl_del_reparse_point`. Internal helpers include `fsctl_get_reparse_point_reg` for stored `SAMBA_XATTR_REPARSE_ATTRIB` xattrs, `fsctl_get_reparse_point_int` for marshalling `struct reparse_data_buffer`, special-file helpers for FIFO/socket/block/char devices using `IO_REPARSE_TAG_NFS`, and `fsctl_get_reparse_point_lnk` for symlink reparse data via `parent_pathref` and `read_symlink_reparse`.

## Control Flow
Get starts by requiring `FILE_ATTRIBUTE_REPARSE_POINT` from `fdos_mode`, then dispatches on `st_ex_mode & S_IFMT`. Regular files read the reparse xattr; special Unix objects synthesize NFS reparse buffers; symlinks read link-specific reparse metadata. The result is validated with `reparse_buffer_check` before returning tag, bytes, and length. Set validates that the handle is a writable regular file, checks incoming reparse data, rejects tag replacement with a different existing tag, writes the xattr, and updates DOS attributes. Delete requires a writable handle, validates the existing tag and an empty-data delete buffer, removes the xattr, and clears the DOS reparse bit.

## State And Persistence
Regular-file reparse data is persisted in `SAMBA_XATTR_REPARSE_ATTRIB`. DOS attributes are updated through `SMB_VFS_FSET_DOS_ATTRIBUTES` and mirrored into `fsp->fsp_name->st.cached_dos_attributes`. Special-file get paths synthesize data from stat information and do not persist new state.

## Dependencies And Integration Points
The file depends on `libcli/smb/reparse.h`, `source3/smbd/proto.h`, VFS xattr and DOS attribute operations, stat data in `files_struct`, Unix major/minor helpers, symlink reparse helpers, talloc, and NTSTATUS/errno mapping. It is called by SMB FSCTL handling when clients query or manipulate reparse points.

## Risks
Set/delete access checks depend on `SEC_FILE_WRITE_DATA | SEC_FILE_WRITE_ATTRIBUTE` and `twrp`, so incorrect handle state can expose or reject operations. Tag mismatch handling must preserve Windows semantics. `fsctl_get_reparse_point_reg` bounds allocation to 64 KiB plus header and returns `BUFFER_TOO_SMALL` on `ERANGE`; callers must retry correctly. DOS attribute and xattr updates are not rolled back as a transaction if one succeeds and the other fails.

## Test Signals
Useful tests include regular-file set/get/delete, tag mismatch rejection, too-small output buffers, readonly handle denial, invalid reparse buffers, special FIFO/socket/device synthesis, symlink reparse reads, and DOS attribute cache updates after set/delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.c -->
