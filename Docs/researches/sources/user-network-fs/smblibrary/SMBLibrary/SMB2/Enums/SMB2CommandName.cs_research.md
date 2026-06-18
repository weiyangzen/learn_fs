<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2CommandName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2CommandName.cs

Purpose: Defines SMB2 command identifiers for SMB2 wire packet fields.

Important APIs/types/functions: `SMB2CommandName` maps protocol constants for negotiate through oplock break command numbers.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by base request/response dispatcher and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2CommandName.cs -->
