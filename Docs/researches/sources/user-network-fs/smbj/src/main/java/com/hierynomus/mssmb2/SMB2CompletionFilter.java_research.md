<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 46-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2CompletionFilter implements EnumWithValue<SMB2CompletionFilter>`; wire values: `FILE_NOTIFY_CHANGE_FILE_NAME`, `FILE_NOTIFY_CHANGE_DIR_NAME`, `FILE_NOTIFY_CHANGE_ATTRIBUTES`, `FILE_NOTIFY_CHANGE_SIZE`, `FILE_NOTIFY_CHANGE_LAST_WRITE`, `FILE_NOTIFY_CHANGE_LAST_ACCESS`, `FILE_NOTIFY_CHANGE_CREATION`, `FILE_NOTIFY_CHANGE_EA`, `FILE_NOTIFY_CHANGE_SECURITY`, `FILE_NOTIFY_CHANGE_STREAM_NAME`, `FILE_NOTIFY_CHANGE_STREAM_SIZE`, `FILE_NOTIFY_CHANGE_STREAM_WRITE`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2CompletionFilter.java -->
