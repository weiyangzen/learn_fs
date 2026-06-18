# sources/user-network-fs/nfs-utils/support/junction/junction-internal.h

## Purpose
Private libjunction declarations for trusted xattr names, XML tag names, filesystem helpers, and XML helper functions.

## Important APIs, Types, and Functions
Defines `JUNCTION_XATTR_NAME_MODE`, `JUNCTION_XATTR_NAME_NFS`, XML root/fileset/savedmode names, and prototypes for path, xattr, mode, and XML parse/write helpers.

## Control Flow
Implementation files include this header to share internal routines. Public callers use `junction.h` instead.

## State and Persistence Behavior
No state. Constants name persistent trusted xattrs and XML elements.

## Dependencies and Integration Points
Depends on libxml2 tree/xpath/parser headers and `FedFsStatus` from public declarations.

## Risks and Edge Cases
Changing xattr or XML names breaks existing on-disk junctions. Private prototypes must remain aligned with implementation files.

## Test Signals
Build libjunction and run add/get/delete junction round trips against existing xattr names.
