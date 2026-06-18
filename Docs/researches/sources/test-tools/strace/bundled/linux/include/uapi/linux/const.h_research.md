# sources/test-tools/strace/bundled/linux/include/uapi/linux/const.h

Purpose: provides kernel UAPI helper macros for defining constants that work in both C and assembly contexts, plus common alignment and division helpers.

Important APIs/types/functions: `_AC`, `_AT`, `_UL`, `_ULL`, `_BITUL`, `_BITULL`, `_BIT128`, `__ALIGN_KERNEL`, `__ALIGN_KERNEL_MASK`, `__KERNEL_DIV_ROUND_UP`, and `__KERNEL_DIV_ROUND_CLOSEST`.

Control flow: most behavior is macro expansion. In assembly mode constants are left untyped; in C mode suffixes/casts are applied. `__KERNEL_DIV_ROUND_CLOSEST` evaluates its operands into temporaries and chooses add-half or subtract-half rounding based on signedness and operand signs.

State and persistence behavior: there is no runtime state. The persistent effect is compile-time ABI constant shape and type width, especially for bit masks shared by many UAPI headers.

Dependencies: relies on compiler extensions such as `__typeof__`, statement expressions, token pasting, and `unsigned __int128` where `_BIT128` is available.

Integration points: headers such as `devlink.h` use `_BITUL` to define bit masks. Strace indirectly depends on these definitions when bundled UAPI headers generate decoder constants.

Risks: macro side effects are mostly controlled in `DIV_ROUND_CLOSEST`, but inputs to other macros can still be expression-sensitive. `_BIT128` is C-only and intentionally unavailable in assembly. Incorrect signedness assumptions can produce surprising rounding for unsigned negative-like values.

Test signals: compile tests should cover C and assembly preprocess paths, 32/64-bit builds, `_BITUL`/`_BITULL` width behavior, and signed versus unsigned `__KERNEL_DIV_ROUND_CLOSEST` cases.
