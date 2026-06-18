# File Research: sources/os/linux/linux-stable/fs/udf/symlink.c

## Summary
Decodes UDF pathComponent-encoded symbolic links into normal path strings for page-cache symlink access and reports decoded symlink length through getattr.

## Main Responsibilities
- Converts UDF path components to `/`, `../`, `./`, or converted filename components.
- Reads symlink payload from inline inode data or block zero.
- Rejects symlinks longer than one filesystem block.
- Implements symlink address-space operations and inode operations.

## Important Behavior
`udf_pc_to_char()` reserves a terminating NUL, appends separators after filename components, and trims the final separator. Component type 1 with an identifier is ignored as an implementation-defined target.

`udf_symlink_getattr()` reports decoded string length, not raw encoded `i_size`, because UDF symlink encoding is not byte-for-byte POSIX link text.

## Risks
Malformed component lengths or filename conversion failures surface as `-EIO`, `-EINVAL`, or `-ENAMETOOLONG`. Only one-block symlinks are supported.
