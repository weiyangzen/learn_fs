# sources/user-network-fs/nfs-utils/support/junction/nfs.c

## Purpose
Implements NFS junction creation, deletion, validation, XML serialization, and XML parsing for NFSv4 fs_locations data stored in a directory trusted xattr.

## Important APIs, Types, and Functions
Public APIs are `nfs_add_junction()`, `nfs_delete_junction()`, `nfs_get_locations()`, `nfs_is_prejunction()`, and `nfs_is_junction()`. Many helpers convert each `nfs_fsloc` field to/from XML children and attributes under `/junction/fileset/location`.

## Control Flow
Adding a junction verifies the path is a directory that is not already marked, builds an XML document with saved mode and fileset locations, writes it to `trusted.junction.nfs`, then saves mode and marks sticky/no-execute. Deletion verifies a junction, restores mode, and removes NFS xattr. Querying parses the XML through XPath and constructs linked `nfs_fsloc` results.

## State and Persistence Behavior
Persistent state is XML in `trusted.junction.nfs` plus saved mode/sticky-bit state handled by `junction.c`. Parsed locations are heap-owned by callers. No separate database exists.

## Dependencies and Integration Points
Depends on libxml2, NFSv2 `NFS_PORT`, public/private junction headers, and xattr helpers. Export cache code can discover basic junctions and convert locations into export referrals.

## Risks and Edge Cases
All location XML children are effectively required. Repeated/extraneous elements are ignored. `nfs_parse_nodeset()` appends incorrectly by overwriting `result->nfl_next` instead of tracking the tail, so more than two locations may be lost. One class attribute is parsed twice for `writever`.

## Test Signals
Test add/get/delete round trips, multiple locations, zero-component root paths, missing/invalid XML fields, non-junction directories, pre-existing sticky/xattr markers, mode restore, and malformed port/u8/int attributes.
