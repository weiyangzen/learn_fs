# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_tc.h

## Role

Kernel-only Traditional Chinese byte validation and user-defined area constants for Big5 and EUC-TW/CNS 11643 conversion logic in illumos `kiconv`.

## Structure

- Lines 1-22: CDDL header and Sun copyright.
- Lines 24-33: include guard, C++ linkage wrapper, and `_KERNEL` gating.
- Line 36: `KICONV_TC_IS_BIG5_1st_BYTE(v)` accepts first bytes 0x81-0xfe.
- Lines 39-40: `KICONV_TC_IS_BIG5_2nd_BYTE(v)` accepts 0x40-0x7e or 0xa1-0xfe.
- Line 43: `KICONV_TC_EUCTW_MBYTE` defines 0x8e as the CNS 11643 plane 2-16 introducer byte.
- Line 46: `KICONV_TC_EUCTW_PMASK` defines 0xa0 as the plane-number mask.
- Lines 49-50: `KICONV_TC_IS_EUCTW_1st_BYTE(v)` accepts either 0x8e or a valid EUC byte via shared `KICONV_IS_VALID_EUC_BYTE(v)`.
- Lines 53-57: `KICONV_TC_IS_VALID_EUCTW_SEQ(ib)` validates an EUC-TW byte pointer based on caller-provided `isplane1` and `plane_no` variables. Plane 1 checks byte 1; planes 2-16 check bytes 2 and 3 after the 0x8e introducer and plane byte.
- Lines 59-65: constants for EUC-TW user-defined Unicode range: planes 12/13/14/16 map to U+F0000 through a UTF-8 packed range `0xf3b08080-0xf3b8a88f`.
- Lines 67-73: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- Depends on `KICONV_IS_VALID_EUC_BYTE(v)` from the shared kiconv headers, but does not include that header itself.
- `KICONV_TC_IS_VALID_EUCTW_SEQ(ib)` depends on local variables named `isplane1` and `plane_no` in the caller's scope. This is an implicit macro contract.
- The sequence macro reads bytes from `ib + 1`, `ib + 2`, and `ib + 3`; buffer-length checks must be completed by the caller before use.

## Important Behaviors

- Big5 second byte permits two disjoint ranges, deliberately excluding 0x7f-0xa0.
- EUC-TW plane 1 can be represented as two valid EUC bytes. Planes 2-16 use the multibyte introducer 0x8e followed by a plane byte and two EUC bytes.
- The UDA constants describe a Unicode supplementary private-use range, so conversions using them require UTF-8 packed values larger than three bytes.

## Risks And Gotchas

- `KICONV_TC_IS_VALID_EUCTW_SEQ` is not self-contained; it will not compile unless `isplane1` and `plane_no` exist in scope.
- The sequence macro can read past available input if caller length checks are wrong.
- Byte-validation macros evaluate arguments more than once in some cases and should receive side-effect-free expressions.
- As with the other small regional headers, userland inclusion sees no functional declarations because all definitions are gated by `_KERNEL`.

## Research Notes

Read completely: 73 lines, 2221 bytes.
