<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 155-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2CreateOptions implements EnumWithValue<SMB2CreateOptions>`; wire values: `FILE_DIRECTORY_FILE`, `FILE_WRITE_THROUGH`, `FILE_SEQUENTIAL_ONLY`, `FILE_NO_INTERMEDIATE_BUFFERING`, `FILE_NON_DIRECTORY_FILE`, `FILE_NO_EA_KNOWLEDGE`, `FILE_RANDOM_ACCESS`, `FILE_DELETE_ON_CLOSE`, `FILE_OPEN_FOR_BACKUP_INTENT`, `FILE_NO_COMPRESSION`, `FILE_OPEN_REPARSE_POINT`, `FILE_OPEN_NO_RECALL`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `com.hierynomus.protocol.commons.EnumWithValue`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

offset arithmetic can misparse variable buffers, compounded packets, or directory chains if lengths are untrusted; unknown future enum values may be dropped or mapped to null by generic conversion helpers.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CreateOptions.java -->
