# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConsts.java

## Purpose
`OzoneConsts` is a private constant catalog for Ozone runtime identifiers, metadata keys, URI schemes, ACL symbols, DB names, audit field names, snapshot and container field names, Ranger endpoints, security literals, quota/unit values, and object-key validation. These constants standardize names that are persisted in metadata, exchanged over APIs, or logged.

## Important APIs, types, and functions
- The class is `final`, has only constants, a private constructor, and enum `Units { TB, GB, MB, KB, B }`.
- Cluster/storage identity constants cover SCM, cluster, datanode, storage, layout, ctime, and certificate ids.
- Namespace constants cover Ozone/OFS schemes, RPC/HTTP schemes, root path, URI delimiter, OM key/user/S3 prefixes, and trash/copying suffixes.
- Container and DB constants cover `.container`, checksum sidecar extension, metadata/chunks paths, schema versions, DB names, metadata keys, block delete markers, and checksum fields.
- ACL and audit constants cover ACL entity/action symbols and audit map keys for volumes, buckets, keys, quotas, replication, multipart upload, tenants, snapshots, and job status.
- Snapshot and RocksDB constants cover checkpoint/snapshot directories, transaction info, prepare markers, compaction backup/log tables, SST suffixes, and snapshot diff DB names.
- Security and Ranger constants cover Kerberos values, delegation token fields, SCM CA naming, Ranger REST endpoints, and tenant policy/role suffixes.
- `KEYNAME_ILLEGAL_CHARACTER_CHECK_REGEX` defines the allowed object key character pattern.

## Control flow
There is no dynamic control flow. Static initialization constructs `ROOT_PATH`, `SCM_ROOT_CA_COMPONENT_NAME`, and the key-name validation `Pattern`.

## State and persistence behavior
The constants are immutable, but many values are persistence-critical because they become RocksDB keys, marker filenames, metadata YAML fields, audit keys, HTTP endpoints, and object namespace delimiters. Changing them can make existing data unreadable or alter API behavior.

## Dependencies and integration points
Dependencies are light: HDDS `InterfaceAudience`, Java `Path/Paths`, charset constants, and regex `Pattern`. Integration spans OM, SCM, DataNode containers, S3 gateway, Ranger, audit logging, snapshots, compaction, and filesystem clients.

## Risks and edge cases
- Persistence and wire/API constants require strict backward compatibility.
- `KEYNAME_ILLEGAL_CHARACTER_CHECK_REGEX` is an allow-list; changes affect object name validation and S3 compatibility.
- Constants encode several sentinel values, such as `QUOTA_RESET`, `OLD_QUOTA_DEFAULT`, `DEFAULT_OM_UPDATE_ID`, and `EXPECTED_GEN_CREATE_IF_ABSENT`; misuse can invert semantics.
- Several strings include separators such as `/`, `$`, `#`, tab, and `:` that must match database key composition and parsing logic exactly.

## Test signals
Tests should verify DB key construction/parsing, persisted marker lookup, audit map field names, key-name validation, quota sentinel handling, URI scheme handling, Ranger endpoint composition, and backward compatibility against known metadata samples.
