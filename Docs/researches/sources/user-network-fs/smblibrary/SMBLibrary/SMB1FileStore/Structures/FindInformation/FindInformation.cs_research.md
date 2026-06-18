<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformation.cs

Purpose: Abstract base for SMB1 find-information records and factory for decoding records by information level.

Important APIs/types/functions: `NextEntryOffset`, abstract `WriteBytes`, `GetLength`, `InformationLevel`, and static `ReadEntry` define the common contract.

Control flow: `ReadEntry` switches on `FindInformationLevel` and instantiates the matching concrete record at the supplied buffer offset and Unicode mode.

State and persistence behavior: No persistent state beyond the common link offset field stored on each entry.

Dependencies and integration points: Integration point for `FindInformationList`, helper conversions, and SMB1 transaction parsers that need polymorphic find entries.

Risks and edge cases: Unsupported levels throw. The factory does not validate structure size before dispatch; concrete constructors are responsible for consuming the expected layout.

Test signals: Tests should assert dispatch for each supported level and exception behavior for unsupported levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformation.cs -->
