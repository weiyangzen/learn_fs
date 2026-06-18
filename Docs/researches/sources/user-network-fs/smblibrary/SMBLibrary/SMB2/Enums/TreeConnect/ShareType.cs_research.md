<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareType.cs

Purpose: Defines tree-connect share type values for SMB2 wire packet fields.

Important APIs/types/functions: `ShareType` maps protocol constants for disk, pipe, and print shares.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `TreeConnectResponse.ShareType` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareType.cs -->
