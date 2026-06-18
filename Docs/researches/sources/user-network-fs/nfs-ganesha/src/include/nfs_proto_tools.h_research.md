# sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_tools.h

## Purpose

`nfs_proto_tools.h` declares protocol utility helpers for NFSv3 WCC/attributes, NFSv4 attribute bitmap encoding/decoding, UTF-8/path validation, FSAL attribute conversion, response-size accounting, pNFS layout return, mounted-on fileid, quotas, and optional NFSACL conversion.

## Important APIs, Types, and Functions

`fattr4_dent_t` and `fattr4tab` describe each NFSv4 attribute's name, support/encode flags, size, access, FSAL masks, and encode/decode/compare callbacks. Inline bitmap helpers scan/set/clear/check attributes and special WRONGSEC/rdattr_error cases. Utility APIs include NFSv3 WCC setters, `nfs_RetryableError`, `nfs3_Sattr_To_FSAL_attr`, `nfs4_Fattr_Free`, `file_To_Fattr`, access/support/compare checks, FSAL/NFS attr conversion, error fattr filling, readdir entry encoding, unsupported-attr removal, path UTF-8 scanning, pathname alloc/free, response room checks, mounted-on fileid, and optional POSIX ACL encode/decode.

## Control Flow

NFSv3 handlers build pre/post/WCC attributes around FSAL operations. NFSv4 GETATTR/SETATTR/VERIFY/NVERIFY and READDIR use bitmaps to decide which attributes to encode/decode, convert FSAL attributes through `fattr4tab`, enforce UTF-8/path rules, and guard response size.

## State and Persistence Behavior

Most helpers are stateless conversions. They may read config flags such as delay-error dropping and UTF-8 enforcement, and they mutate FSAL attrlists or response buffers. Persistent filesystem state changes only when converted setattr/ACL data reaches FSAL operations.

## Dependencies and Integration Points

It depends on hashtables, logging, file handles, SAL data, FSAL APIs, optional POSIX ACLs, and NFS parameters. It is central to NFSv3/v4 protocol handlers, readdir encoding, ACL support, quotas, and pNFS layout handling.

## Risks and Test Signals

Risks include bitmap off-by-one errors beyond three words, unsupported attribute leakage, wrong attr access classification, UTF-8 validation bypass, response-size undercount, WCC values from stale attrs, and ACL conversion loss. Tests should cover bitmap iteration, all `fattr4tab` entries, setattr conversion, GETATTR errors, readdir encoded entries, path filter flags, response room exhaustion, retryable FSAL errors, and POSIX ACL round trips when enabled.
