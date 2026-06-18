# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/UTimeHelper.cs

- **Purpose:** UTime - The number of seconds since Jan 1, 1970, 00:00:00. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 82 lines, 2604 bytes. Namespace `SMBLibrary.SMB1`. Primary type `UTimeHelper`.
- **Important APIs/types/functions:** Types: class UTimeHelper. Constructors: none. Constants/static metadata: MinUTimeValue. Fields/properties: none detected. Methods/overrides: ReadUTime, ReadNullableUTime, WriteUTime.
- **Control flow:** UTIME fields are converted between SMB seconds-since-1970 values and nullable DateTime values.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: UTimeHelper. Wire helpers observed: LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt32.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
