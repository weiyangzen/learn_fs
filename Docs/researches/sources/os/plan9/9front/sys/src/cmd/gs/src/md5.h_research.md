# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.h

## Purpose
Public header for the standalone MD5 implementation.

## Main Content
- Defines `md5_byte_t` as `unsigned char`.
- Defines `md5_word_t` as `unsigned int`.
- Defines `md5_state_t` with bit count, four-word digest buffer, and 64-byte partial block buffer.
- Declares `md5_init`, `md5_append`, and `md5_finish`, wrapped in `extern "C"` for C++.

## Integration Notes
- Documents optional `ARCH_IS_BIG_ENDIAN` behavior for compile-time byte-order specialization.

## Risks and Edge Cases
- Assumes `unsigned int` is 32 bits, matching the intended Ghostscript-era target assumptions.
- Header is generic and not Ghostscript-specific, but `lib.mak` wraps compilation for Ghostscript include ordering.
