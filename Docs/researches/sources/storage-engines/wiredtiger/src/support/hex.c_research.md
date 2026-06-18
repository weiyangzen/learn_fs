# sources/storage-engines/wiredtiger/src/support/hex.c

## Purpose
`hex.c` converts between raw bytes and printable hexadecimal or escaped-hex strings, and provides bounded diagnostic dumping of raw buffers. It supports logging, debugging, metadata display, and APIs that need textual byte encodings.

## Important APIs, Types, and Functions
`__wt_fill_hex` wraps the inline `__fill_hex` raw-to-hex converter. `__wt_log_data_dump` logs a formatted preamble and a hex dump in 1 KiB chunks, capped at 64 KiB. `__wt_raw_to_hex` and `__wt_raw_to_esc_hex` convert raw data into `WT_ITEM` buffers. `__wti_hex2byte` parses two hex characters into one byte. `__wt_hex_to_raw`, `__wt_nhex_to_raw`, and `__wt_esc_hex_to_raw` parse printable encodings back into raw bytes. `__hex_fmterr` centralizes invalid-hex errors.

## Control Flow
Raw-to-hex reserves one byte for NUL termination and emits two hex digits per source byte while capacity remains. Escaped-hex keeps printable characters as-is, doubles literal backslashes, and emits backslash plus two hex digits for non-printable bytes. Raw hex parsing rejects odd-length inputs, initializes an output buffer at half the input size, then decodes pairs. Escaped parsing copies ordinary bytes and decodes backslash escapes unless the escape is a doubled backslash.

## State and Persistence Behavior
The functions mutate caller-provided `WT_ITEM` buffers or temporary scratch buffers. No persistent state is maintained. `__wt_log_data_dump` allocates scratch items for the preamble and chunk text and frees them on all paths.

## Dependencies and Integration Points
The file uses WiredTiger buffer allocation, scratch buffers, printf-style buffer formatting, logging through `__wt_errx`, character classification, and `__wt_hex`. It is used by debug and logging paths and by higher-level serialization code that needs printable byte strings.

## Risks
The length reported by `__fill_hex` includes the terminating NUL because it measures after writing it; callers must understand that convention. Size calculations like `size * 2 + 1` and `size * 3 + 1` require upstream sizes to be reasonable enough not to overflow `size_t`. `__wt_log_data_dump` intentionally truncates large dumps, so logs are diagnostic rather than complete evidence for very large buffers. Escaped parsing treats malformed or incomplete escapes as format errors.

## Test Signals
Tests should round-trip raw hex and escaped hex over empty input, printable ASCII, backslash, NUL bytes, high-bit bytes, odd-length hex, invalid hex characters, and incomplete escapes. Logging tests should verify empty-buffer output, chunk boundaries at 1024 bytes, and truncation after 64 KiB. Buffer tests should check NUL termination and reported sizes.
