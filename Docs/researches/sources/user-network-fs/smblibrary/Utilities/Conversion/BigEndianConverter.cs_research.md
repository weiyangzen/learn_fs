# sources/user-network-fs/smblibrary/Utilities/Conversion/BigEndianConverter.cs

Purpose: `BigEndianConverter` performs explicit big-endian conversions between byte arrays and integer/GUID values.

Important APIs/types/functions: `ToUInt16/Int16`, `ToUInt32/Int32`, `ToUInt64/Int64`, `ToGuid`, and `GetBytes` overloads for those types. GUID handling reverses the first three GUID fields on little-endian hosts to produce big-endian wire bytes.

Control flow: numeric reads combine shifted bytes; writes mask shifted values into byte arrays; GUID writes start from `Guid.ToByteArray()` and conditionally swap field bytes.

State and persistence behavior: stateless.

Dependencies and integration points: used by big-endian readers/writers and AES-CCM associated-data length encoding.

Risks: no bounds checks beyond runtime exceptions. `ToUInt32` shifts `byte` values as signed `int` before casting to `uint`, which still yields intended two's complement values but is subtle. GUID byte order is easy to misuse because .NET GUID layout differs from string/network layout.

Test signals: fixed vectors for integers and GUIDs, cross-platform tests for `BitConverter.IsLittleEndian`, and round trips through `BigEndianReader/Writer`.
