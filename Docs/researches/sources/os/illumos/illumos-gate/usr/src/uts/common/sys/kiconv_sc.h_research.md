# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_sc.h

## Role

Kernel-only Simplified Chinese byte validation and boundary constants for GBK, GB2312, and GB18030 conversion logic in illumos `kiconv`.

## Structure

- Lines 1-22: CDDL header and Sun copyright.
- Lines 24-33: include guard, C++ linkage wrapper, and `_KERNEL` gating.
- Line 36: `KICONV_SC_IS_GBK_1st_BYTE(c)` accepts first bytes 0x81-0xfe.
- Lines 39-40: `KICONV_SC_IS_GBK_2nd_BYTE(c)` accepts 0x40-0x7e or 0x80-0xfe.
- Line 43: `KICONV_SC_IS_GB18030_2nd_BYTE(c)` accepts decimal digit bytes 0x30-0x39 for four-byte GB18030 sequences.
- Line 46: `KICONV_SC_IS_GB18030_3rd_BYTE(c)` accepts 0x81-0xfe.
- Lines 49-50: `KICONV_SC_IS_GB18030_4th_BYTE(c)` aliases the four-byte second-byte digit rule.
- Lines 53-60: `KICONV_SC_GET_GB_LEN(v, l)` sets `l` to 4, 2, or 1 based on whether high 16 or high 8 bits are present in a packed GB value.
- Line 62: `KICONV_SC_IS_GB2312_BYTE(b)` accepts 0xa1-0xfe.
- Lines 65-69: constants for the Unicode plane-1/GB18030 arithmetic boundary: U+10000, its UTF-8 packed bytes `0xf0908080`, and GB18030 sequence `0x90308130`.
- Lines 71-77: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- This header has no includes. It relies only on basic integer comparisons and is intended to be included after any broader kiconv declarations needed by the consumer.
- The length macro assumes a packed integer representation where one-byte, two-byte, and four-byte GB sequences occupy low-order bytes.
- Plane-1 constants are used by GB18030 arithmetic conversion for Unicode code points at and above U+10000.

## Important Behaviors

- The first/second byte validators labeled GBK are also used for the two-byte subset of GB18030.
- Four-byte GB18030 validation has the pattern first byte 0x81-0xfe, second digit 0x30-0x39, third 0x81-0xfe, fourth digit 0x30-0x39.
- `KICONV_SC_GET_GB_LEN` is a statement macro that assigns to an output lvalue rather than returning a value.

## Risks And Gotchas

- `KICONV_SC_GET_GB_LEN(v, l)` lacks `do { } while (0)`, so it is unsafe in some `if/else` contexts unless wrapped by the caller.
- The length macro evaluates `v` more than once. Side-effect expressions would be problematic.
- The byte validators do not cast to unsigned. If callers pass signed `char` values with negative representation, validation can fail unexpectedly unless values are normalized to unsigned/integer byte range.

## Research Notes

Read completely: 77 lines, 2429 bytes.
