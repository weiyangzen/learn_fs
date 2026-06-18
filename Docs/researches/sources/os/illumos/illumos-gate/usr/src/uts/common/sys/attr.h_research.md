# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/attr.h

## Purpose

`attr.h` defines illumos extended system attribute names, command-line option aliases, attribute IDs, and helper APIs.

## Main Content

String constants cover attributes such as creation time, hidden, system, readonly, archive, nounlink, immutable, appendonly, nodump, opaque, antivirus quarantine/modified/scanstamp, fsid, owner/group SID, reparse point, generation, offline, and sparse.

Option strings map many of those attributes to compact utility flags. `f_attr_t` enumerates the same attributes, ending in `F_ATTR_ALL`.

`xattr_view_t` identifies virtual system attribute directory views: readonly and readwrite. `xattr_entry_t` maps an attribute name to an option, xattr view, and nvlist data type.

## Kernel and User Helpers

Kernel builds define `xattr_fid_t` for virtual sysattr fid handling and declare `xattr_dir_vget()` and `xattr_sysattr_casechk()`. Common helpers map attributes to names, options, views, and data types.

## Research Notes

This is directly filesystem-relevant. It defines the names and metadata used by extended attributes and virtual system attribute directories.
