<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/OplockLevel.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/OplockLevel.cs

Purpose: Defines oplock level values for SMB2 wire packet fields.

Important APIs/types/functions: `OplockLevel` maps protocol constants for none, level II, exclusive, batch, and lease.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by create request/response oplock fields and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/OplockLevel.cs -->
