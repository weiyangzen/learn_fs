# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/itoa.h

Purpose: This header implements fast integer-to-decimal conversion helpers for writer output and pointer index stringification.

Important APIs and functions: `GetDigitsLut()` returns a 200-byte lookup table for pairs `"00"` through `"99"`. `u32toa`, `i32toa`, `u64toa`, and `i64toa` write decimal digits into a caller-supplied buffer and return the end pointer.

Control flow: Unsigned conversions split values into groups of two, four, eight, or sixteen decimal digits to minimize divisions and branches. Signed conversions emit `'-'` and convert through two's-complement negation (`~u + 1`) to handle minimum signed values without overflow. No null terminator is appended by these functions.

State and persistence behavior: There is no mutable state. The LUT is a static const array. Output is written only into the caller's buffer.

Dependencies and integration points: It includes `rapidjson.h`. `writer.h` uses it for integer JSON numbers, `dtoa.h` uses the LUT for exponent writing, and `pointer.h` uses it to construct array-index token names in `Append(SizeType)`.

Risks: Caller buffer sizing is critical: 32-bit signed values need up to 11 chars and 64-bit signed values up to 20 plus sign. Functions do not append `'\0'`, so callers that need strings must do so themselves. Threshold branches must preserve leading-zero behavior inside grouped suffixes.

Test signals: Verify min/max signed and unsigned 32/64-bit values, every digit-count threshold, zero, negative minimum values, no unintended leading zeros, and pointer append stringification for `SizeType` width.
