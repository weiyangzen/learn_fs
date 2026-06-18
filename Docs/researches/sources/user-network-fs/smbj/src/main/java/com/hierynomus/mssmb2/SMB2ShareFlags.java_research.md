<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 50-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2ShareFlags implements EnumWithValue<SMB2ShareFlags>`; wire values: `SMB2_SHAREFLAG_MANUAL_CACHING`, `SMB2_SHAREFLAG_AUTO_CACHING`, `SMB2_SHAREFLAG_VDO_CACHING`, `SMB2_SHAREFLAG_NO_CACHING`, `SMB2_SHAREFLAG_DFS`, `SMB2_SHAREFLAG_DFS_ROOT`, `SMB2_SHAREFLAG_RESTRICT_EXCLUSIVE_OPENS`, `SMB2_SHAREFLAG_FORCE_SHARED_DELETE`, `SMB2_SHAREFLAG_ALLOW_NAMESPACE_CACHING`, `SMB2_SHAREFLAG_ACCESS_BASED_DIRECTORY_ENUM`, `SMB2_SHAREFLAG_FORCE_LEVELII_OPLOCK`, `SMB2_SHAREFLAG_ENABLE_HASH_V1`, `SMB2_SHAREFLAG_ENABLE_HASH_V2`, `SMB2_SHAREFLAG_ENCRYPT_DATA`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2ShareFlags.java -->
