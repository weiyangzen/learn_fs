<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/DerEncodingHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/DerEncodingHelper.cs

## Purpose
`DerEncodingHelper` centralizes the subset of ASN.1 DER length/string handling needed by SPNEGO token readers and writers.

## Important APIs and Types
`DerEncodingTag` names the tags used by this implementation: octet string, object identifier, enum, general string, and sequence. `ReadLength()` and `WriteLength()` implement short and long-form DER lengths. `GetLengthFieldSize()` predicts encoded length size for buffer allocation. `EncodeGeneralString()` and `DecodeGeneralString()` map SPNEGO hint names to ASCII bytes.

## Control Flow
Readers consume from a caller-owned offset by reference, interpreting long-form length bytes as big-endian. Writers build long-form fields by repeatedly taking base-256 bytes, reversing, and prefixing with `0x80 | lengthField.Length`; short lengths are written as a single byte.

## State, Dependencies, and Integration
The class is stateless and relies on `ByteReader`/`ByteWriter`. SPNEGO init, init2, response, and generic token wrappers use it for exact buffer sizing before serialization.

## Risks and Test Signals
No bounds or canonical-DER checks are performed here; callers depend on lower-level readers to throw when offsets exceed buffers. Indefinite length is not supported, which is correct for DER but should be tested. Use round-trip tests for lengths around 127, 128, 255, 256, and multibyte values, plus malformed/truncated SPNEGO input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/DerEncodingHelper.cs -->
