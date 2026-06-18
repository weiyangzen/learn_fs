# sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteUtils.cs

Purpose: `ByteUtils` contains small byte-array and stream utilities shared by serialization and cryptography helpers.

Important APIs/types/functions: `Concatenate`, `AreByteArraysEqual`, `XOR` overloads, and `CopyStream` overloads with optional byte count.

Control flow: concatenation allocates and copies two arrays; equality compares length then bytes; XOR validates equal lengths or offset ranges and returns a newly allocated result; stream copy loops with up to a 1 MB buffer until count or EOF.

State and persistence behavior: stateless, but copies data from input streams to output streams and consumes stream position.

Dependencies and integration points: used by `ByteReader`, `AesCcm`, `AesCmac`, and other byte protocol code.

Risks: `AreByteArraysEqual` is not constant-time, so using it for authentication tags leaks timing information. `CopyStream` with a count of zero creates a zero-length buffer but does not read; with huge counts it loops until EOF. Null arrays are not handled.

Test signals: tests should cover XOR ranges, unequal length exceptions, copy limits, EOF before requested count, equality mismatch positions, and cryptographic call sites that need constant-time comparison.
