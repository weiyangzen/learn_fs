# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ko.h

## Role

Kernel-only Korean encoding helper macros for EUC-KR, UHC, and Korean user-defined area handling in illumos `kiconv`.

## Structure

- Lines 1-22: CDDL header and Sun copyright.
- Lines 24-33: include guard, C++ linkage wrapper, and `_KERNEL` gating.
- Line 36: `KICONV_KO_IS_EUCKR_BYTE(b)` validates an EUC-KR byte in the 0xa1-0xfe range.
- Lines 39-43: UHC byte validators. First byte is 0x81-0xfe. Second byte is 0x41-0x5a, 0x61-0x7a, or 0x81-0xfe.
- Lines 46-56: constants for Korean user-defined areas in EUC-KR: segment 1 `0xc9a1-0xc9fe`, segment 2 `0xfea1-0xfefe`, segment bytes `0xc9` and `0xfe`, offset range `0xa1-0xfe`, range size `0x5e`, and conversion offsets `0xf65f`/`0xf6bd`.
- Lines 59-62: corresponding Unicode private-use/UDA range constants: UCS-4 `0xf700-0xf7bb`, UTF-8 scalar-packed `0xef9c80-0xef9ebb`.
- Lines 65-69: `KICONV_KO_IS_UDC_IN_EUC(v)` detects whether a packed EUC-KR two-byte value falls in either UDC segment.
- Lines 72-74: `KICONV_KO_IS_UDC_IN_UTF8(v)` detects whether a packed UTF-8 value falls in the Korean UDA range.
- Lines 76-82: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- This header does not include `<sys/kiconv.h>` itself. It assumes consumers include any needed base kiconv definitions separately.
- The UDC macros operate on packed integer representations, not byte pointers. For example, EUC-KR bytes must be combined into values such as `0xc9a1`.
- The UTF-8 constants are packed byte sequences in an integer, matching the style used elsewhere in kiconv tables.

## Important Behaviors

- UHC second-byte validation intentionally includes ASCII letter ranges and the high-byte range, excluding punctuation gaps such as 0x5b-0x60 and 0x7b-0x80.
- EUC-KR validation accepts only graphic EUC bytes 0xa1-0xfe; ASCII handling is outside these macros.
- The Korean UDA mapping spans two EUC rows of 94 entries each, totaling `0xbc` code positions, mapped to U+F700 through U+F7BB.

## Risks And Gotchas

- Macro arguments are evaluated more than once in range checks like `KICONV_KO_IS_UDC_IN_EUC(v)`. Callers should pass side-effect-free expressions.
- Because there are no parentheses around each `&&` subexpression inside `KICONV_KO_IS_UHC_2nd_BYTE`, standard C precedence still gives the intended meaning, but the macro relies on that precedence.
- The header is public under `sys/` but meaningful only under `_KERNEL`; userland inclusion yields only guards and C++ wrappers.

## Research Notes

Read completely: 82 lines, 2690 bytes.
