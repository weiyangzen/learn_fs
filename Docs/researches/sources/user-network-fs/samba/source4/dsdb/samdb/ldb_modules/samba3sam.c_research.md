# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba3sam.c

## Purpose
`samba3sam.c` implements the `samba3sam` LDB map module, a compatibility layer that presents Samba4-style SAM attributes over a Samba3 LDAP backend schema. It maps object classes, renames attributes, converts SID and password-hash formats, generates primary group fields, and ignores many AD-only attributes that cannot be represented in the Samba3 schema.

## Important APIs, Types, And Functions
Conversion helpers include `generate_primaryGroupID()` and `generate_sambaPrimaryGroupSID()` for translating between `primaryGroupID` and `sambaPrimaryGroupSID`; `convert_uid_samaccount()` for `sAMAccountName` from `uid`; `lookup_homedir()`, `lookup_gid()`, and `lookup_uid()` for POSIX passwd-derived fields; `encode_sid()` and `decode_sid()` for textual `sambaSID` to binary `objectSid`; and `bin2hex()`/`hex2bin()` for Samba password hashes.

`samba3_objectclasses[]` maps local classes such as `user`, `group`, and `domain` to remote `posixAccount`, `posixGroup`, `sambaGroupMapping`, `sambaSAMAccount`, and `sambaDomain`. `samba3_attributes[]` is the main mapping table, using `LDB_MAP_RENAME`, `LDB_MAP_CONVERT`, `LDB_MAP_GENERATE`, `LDB_MAP_KEEP`, and `LDB_MAP_IGNORE`. `samba3sam_init()` calls `ldb_map_init()`. The file also registers `show_deleted_ignore`, a small test-support module that marks show-deleted and show-recycled controls non-critical before passing searches down.

## Control Flow
The runtime control flow is mostly supplied by the generic `ldb_map` framework. During module init, Samba registers the object-class and attribute maps under the `samba3sam` name. For mapped searches and updates, the framework invokes the declared converters and generators. SID conversions use NDR push/pull of `struct dom_sid`; password conversions use smbpasswd helper functions for 16-byte hash to 32-hex-character conversion.

Generated `primaryGroupID` parses the RID suffix from `sambaPrimaryGroupSID`. Generated `sambaPrimaryGroupSID` pulls the domain SID from binary `objectSid`, removes the final RID authority, and appends `primaryGroupID`. POSIX-derived conversions call `getpwnam()` based on `unixName`/`uid` input and return empty values on lookup failure.

## State And Persistence
The module itself has no durable state. Persistent reads and writes go to the remote Samba3-compatible LDAP backend through the mapping layer. Conversion outputs are request-scoped talloc values. Calls to `getpwnam()` depend on local NSS state, so results can vary with system account configuration rather than directory contents alone.

## Dependencies And Integration Points
This file depends on `ldb_map`, POSIX passwd APIs, NDR security structures, DOM SID utilities, SAMR password hash structures, and Samba3 helper functions. It integrates with tests and migration paths that need Samba4 LDAP semantics over old Samba3 schemas rather than the normal DSDB module stack.

## Risks And Test Signals
The largest risks are lossy mappings and local NSS dependency. Many AD attributes are ignored, so callers may believe writes succeeded even though the Samba3 backend cannot persist the fields. `generate_sambaPrimaryGroupSID()` mutates the decoded SID by decrementing `num_auths`, which assumes a normal domain SID plus RID layout. Password hash conversion must reject malformed lengths and invalid hex. Tests should cover object-class mapping, SID encode/decode, primary group generation in both directions, hash conversion round-trips, missing `getpwnam()` entries, ignored attribute behavior, and show-deleted/show-recycled control criticality handling for the test module.
