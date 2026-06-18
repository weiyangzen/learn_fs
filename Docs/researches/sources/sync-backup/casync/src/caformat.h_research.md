# sources/sync-backup/casync/src/caformat.h

## Purpose
Defines the casync archive and index wire format: record type IDs, feature flag bits, default/composite masks, and little-endian C structures for every serialized object.

## Important APIs, Types, and Functions
Archive types include `ENTRY`, `USER`, `GROUP`, `XATTR`, ACL records, `FCAPS`, `QUOTA_PROJID`, `SELINUX`, `SYMLINK`, `DEVICE`, `PAYLOAD`, `FILENAME`, and `GOODBYE`. Index types are `INDEX` and `TABLE`. Feature masks cover UID/name/time/mode/file-type support, DOS and chattr flags, btrfs subvolumes, xattrs, ACLs, SELinux, capabilities, quota IDs, excludes, submount handling, nodump handling, and digest type. Structures include `CaFormatHeader`, `CaFormatEntry`, variable-length metadata payloads, `CaFormatGoodbyeItem/Tail`, `CaFormatIndex`, `CaFormatTableItem`, and `CaFormatTableTail`.

## Control Flow
The header has no executable flow. Its opening comment defines archive record ordering: entry metadata, optional metadata records, payload/symlink/device data, recursive directory children in sorted name order, then a goodbye lookup table.

## State and Persistence Behavior
All structs are persisted with explicit `le64_t` fields and variable-length trailing arrays. `GOODBYE` and `TABLE` tails contain repeated size/marker fields for validation. Composite masks such as `CA_FORMAT_DEFAULT`, `CA_FORMAT_WITH_BEST`, `CA_FORMAT_WITH_UNIX`, `CA_FORMAT_WITH_FUSE`, and `CA_FORMAT_FEATURE_FLAGS_MAX` define compatibility policy.

## Dependencies and Integration Points
Depends on `cachunkid.h` and `util.h`. It is the shared ABI for encoder, decoder, index, feature utilities, and FUSE exposure.

## Risks
Changing constants or layout breaks archive/index compatibility. Variable-length records must be bounds-checked against the provided maximum macros. `CaFormatTable` deliberately uses `UINT64_MAX` table size while being written incrementally, so readers must validate the tail rather than trusting the table header size.

## Test Signals
Golden archive/index fixtures, endian/layout static assertions, max-size validation, decoder rejection of bad markers/sizes, and feature-mask compatibility tests are the key signals.
