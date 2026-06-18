# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/mips.h

This is a generated/derived Ghostscript architecture header for a 32-bit big-endian MIPS-like target.

It defines:
- Scalar alignment requirements for short, int, long, pointer, float, double, and struct values.
- Scalar sizes via log2 constants and explicit pointer/float/double sizes.
- IEEE float/double mantissa sizes.
- Unsigned max-value macros for C scalar types.
- Cache sizes: 4 KiB L1 and 512 KiB L2.
- Platform behavior flags: big-endian, unsigned pointers, IEEE floats, arithmetic right shift behavior, inability to shift a full long width, and negative/positive division truncation.

There is no executable logic and no filesystem interaction. Its role is to let Ghostscript compile platform-sensitive memory, arithmetic, and object-layout code correctly on Plan 9 MIPS builds.
