# sources/storage-engines/wiredtiger/src/include/crypt_header.h

## Purpose
`crypt_header.h` defines the on-disk/in-buffer header used for encrypted key data. It standardizes a signature, version compatibility, payload size, checksum, and optional key-rotation timestamp.

## Important APIs, Types, and Functions
`WT_CRYPT_HEADER` contains `signature`, `version`, `compatible_version`, `header_size`, padding, `crypt_size`, `checksum`, and `timestamp`. Constants define the signature (`WT_CRYPT_HEADER_SIGNATURE`), current version, compatible version, and minimum bytes readers must be able to inspect. `__wt_crypt_header_byteswap` swaps multibyte fields on big-endian builds.

## Control Flow
Writers fill the header before encrypted key payloads. Readers inspect at least `WT_CRYPT_HEADER_MIN_SIZE`, verify signature/version compatibility, then use `header_size` to handle optional fields such as the timestamp. Big-endian systems call the inline byteswap before interpreting numeric fields in host order.

## State and Persistence Behavior
This structure is a durability boundary. `header_size` allows forward-compatible extension, `compatible_version` protects older readers, and `checksum` covers the encrypted payload. The timestamp persists key-rotation ordering when used.

## Dependencies and Integration Points
The header depends on fixed-width integer types and WiredTiger byte-swap helpers. It integrates with the key provider/encryptor path, disaggregated pending encryption-key checkpointing, and any metadata/page-log code that writes encrypted key blobs.

## Risks and Edge Cases
Incorrect endian handling or header-size validation can corrupt key interpretation. Fields beyond `WT_CRYPT_HEADER_MIN_SIZE` must remain optional for older readers. The byteswap helper currently swaps signature, payload size, and timestamp; code handling checksum/version fields must understand which are byte-sized or already treated appropriately.

## Test Signals
Tests should cover reading old version-1-compatible headers, current version headers with timestamps, checksum mismatch handling, short-header rejection, and big-endian serialization through dedicated byte-order tests or cross-platform CI.
