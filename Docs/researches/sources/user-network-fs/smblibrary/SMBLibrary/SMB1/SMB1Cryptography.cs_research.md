# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Cryptography.cs

- **Purpose:** Calculates SMB1 message signatures over signing keys, optional challenge responses, and padded message bytes. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 29 lines, 1124 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Cryptography`.
- **Important APIs/types/functions:** Types: class SMB1Cryptography. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: CalculateSignature.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** Cryptographic state is local to the signature calculation and the returned ulong signature.
- **Dependencies:** Usings: System.Security.Cryptography, Utilities. Local dependencies and referenced protocol types: none. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt64.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first.
- **Test signals:** known SMB1 signing test vectors.
