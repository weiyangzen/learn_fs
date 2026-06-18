<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 38-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2MessageFlag implements EnumWithValue<SMB2MessageFlag>`; wire values: `SMB2_FLAGS_SERVER_TO_REDIR`, `SMB2_FLAGS_ASYNC_COMMAND`, `SMB2_FLAGS_RELATED_OPERATIONS`, `SMB2_FLAGS_SIGNED`, `SMB2_FLAGS_PRIORITY_MASK`, `SMB2_FLAGS_DFS_OPERATIONS`, `SMB2_FLAGS_REPLAY_OPERATION`; state fields: `value`; methods: `getValue`; notable imports: `com.hierynomus.protocol.commons.EnumWithValue`.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageFlag.java -->
