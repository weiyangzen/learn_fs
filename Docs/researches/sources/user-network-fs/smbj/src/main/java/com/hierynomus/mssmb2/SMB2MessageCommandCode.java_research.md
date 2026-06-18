<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 65-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2MessageCommandCode`; wire values: `SMB2_NEGOTIATE`, `SMB2_SESSION_SETUP`, `SMB2_LOGOFF`, `SMB2_TREE_CONNECT`, `SMB2_TREE_DISCONNECT`, `SMB2_CREATE`, `SMB2_CLOSE`, `SMB2_FLUSH`, `SMB2_READ`, `SMB2_WRITE`, `SMB2_LOCK`, `SMB2_IOCTL`, `SMB2_CANCEL`, `SMB2_ECHO`; state fields: `cache`, `value`; methods: `getValue`, `lookup`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

The file depends mainly on sibling SMBJ protocol types. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2MessageCommandCode.java -->
