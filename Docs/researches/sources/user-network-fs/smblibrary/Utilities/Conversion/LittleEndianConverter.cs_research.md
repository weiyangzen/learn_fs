# sources/user-network-fs/smblibrary/Utilities/Conversion/LittleEndianConverter.cs

Purpose: `LittleEndianConverter` performs explicit little-endian conversions for integers, floating-point values, and GUIDs.

Important APIs/types/functions: `ToUInt16/Int16`, `ToUInt32/Int32`, `ToUInt64/Int64`, `ToFloat32`, `ToFloat64`, `ToGuid`, and `GetBytes` overloads for integer and GUID values.

Control flow: integer reads assemble bytes least-significant first; float reads copy bytes and reverse only on non-little-endian hosts before `BitConverter`; GUID reads use little-endian first fields and raw trailing bytes; writes mask shifted values.

State and persistence behavior: stateless.

Dependencies and integration points: used by little-endian readers/writers and UTF-16 null-terminated string reading.

Risks: bounds checks are implicit. Float write helpers are absent, so callers must use other APIs. GUID behavior follows .NET's mixed-endian layout and needs fixed-vector tests.

Test signals: integer, float, and GUID fixed vectors; cross-platform byte-order checks; round trips with reader/writer helpers.
