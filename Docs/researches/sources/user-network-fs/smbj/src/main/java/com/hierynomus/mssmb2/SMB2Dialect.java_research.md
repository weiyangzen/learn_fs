<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java

## Purpose

`sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java` defines SMB2/SMB3 protocol constants as typed enum values with wire numeric values for flag-set and field encoding. The source was read as a complete 66-line file for this research pass.

## Important APIs, Types, and Functions

declaration: `public enum SMB2Dialect`; wire values: `UNKNOWN`, `SMB_2_0_2`, `SMB_2_1`, `SMB_2XX`, `SMB_3_0`, `SMB_3_0_2`, `SMB_3_1_1`; state fields: `value`; methods: `getValue`, `isSmb3x`, `supportsSmb3x`, `lookup`; notable imports: `java.util.Set`.

## Control Flow

There is no branch-heavy logic. Each enum constant carries a protocol value and `getValue` returns it for `EnumWithValue` packing, unpacking, and flag-set conversion helpers.

## State and Persistence Behavior

Enum constants are static protocol metadata. They do not mutate or persist runtime session state.

## Dependencies and Integration Points

Direct dependencies include `java.util.Set`. It sits on the SMBJ protocol core boundary between raw transport bytes and higher-level SMB client operations.

## Risks and Edge Cases

the main risk is semantic drift from the protocol specification or from the callers that assume this type's layout.

## Test Signals

numeric value assertions against the protocol spec and flag-set conversion tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/SMB2Dialect.java -->
