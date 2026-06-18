# File Research: sources/os/linux/linux-stable/fs/smb/common/fscc.h

## Summary
Defines packed structures and constants from MS-FSCC that are shared by SMB client/server code. It is a protocol schema header for reparse data, FSCTL payloads, file information classes, filesystem information classes, attributes, notify records, and POSIX filesystem info.

## Main Content
- Reparse buffers: generic, GUID, mount point, symlink, NFS special file, and WSL symlink formats.
- Server-side clone/copy and allocation structures: `duplicate_extents_to_file`, `duplicate_extents_to_file_ex`, `file_allocated_range_buffer`, query-file-regions request/response, and zero-data request.
- Integrity and disk info structures: get/set integrity info, on-disk volume info, sector-size info, and checksum flags.
- File information records: all-info, basic-info, directory-info variants, EOF info, internal info, link info, rename info, and network-open info.
- Filesystem info classes and records: attribute, control, full-size, size, volume, device, sector, and POSIX information.
- Attribute and capability constants: filesystem capabilities, file attributes and little-endian variants, notify action codes, and POSIX fs info fields.

## Integration Notes
Consumers use these packed layouts to build or parse SMB2/3 query-info, set-info, FSCTL, reparse, directory enumeration, notify, and POSIX extension payloads. Static assertions on rename/link structures protect flexible-array offsets for set-info builders.

## Risks
This header must match wire layouts exactly. Structure packing, endian annotations, flexible arrays, and size comments are part of the ABI. Incorrect constants can break sparse file handling, reparse point parsing, clone/copy, filesystem capability detection, or POSIX extension interpretation.
