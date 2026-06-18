## sources/user-network-fs/gcsfuse/internal/util/test_util.go

Purpose: Shared test helpers for random byte generation and read response flattening.

Important APIs/types/functions: `GenerateRandomBytes(length int)` and `ConvertReadResponseToBytes(data [][]byte, size int)`.

Control flow: random generation fills bytes with uppercase ASCII A-Z using `math/rand`; conversion copies each data slice into a fixed-size buffer in sequence.

State and persistence behavior: uses package-global pseudo-random source; no persistence.

Dependencies and integration points: used by tests that need reproducible-shape byte payloads or flatten chunked read responses.

Risks: random bytes are not cryptographic and are not seeded here. Conversion truncates or leaves zeros according to provided `size`; it does not validate total input length.

Test signals: not directly tested because it is test support code.
