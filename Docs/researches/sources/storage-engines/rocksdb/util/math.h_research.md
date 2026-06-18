# sources/storage-engines/rocksdb/util/math.h

Purpose: provides inline low-level integer math and bit-manipulation helpers used across RocksDB for hashing, range reduction, bit layouts, encoding support, and fast portable operations.

Important APIs/types/functions: defines `BottomNBits`, `FloorLog2`, `ConstexprFloorLog2`, `CountTrailingZeroBits`, `BitsSetToOne`, `BitParity`, `EndianSwapValue`, `ReverseBits`, `DownwardInvolution`, and typed `BitwiseAnd`. It uses BMI2 intrinsics for `BottomNBits` when available, MSVC intrinsics on Windows, and GCC/Clang builtins elsewhere.

Control flow: most functions select an implementation at compile time based on type size and compiler macros. Builtins handle common 16/32/64-bit cases; fallback code handles byte-swapping and MSVC popcount when required. `DownwardInvolution` applies staged xor shifts/masks from high bits to low bits and is documented as an involutive GF(2) transformation with useful bijection properties.

State and persistence behavior: stateless inline utilities with no memory ownership or persistence. Their outputs may become part of persisted formats when used by hashing, filters, or encoding code, so semantic stability matters even though this header writes nothing itself.

Dependencies/integration points: depends on `port/lang.h`, RocksDB namespace setup, compiler intrinsic headers, and standard type traits. `math128.h` specializes several templates for `Unsigned128`, and `hash_test.cc` is the local regression suite.

Risks: several functions have explicit undefined input domains: `BottomNBits` requires `nbits` smaller than the full width, `FloorLog2` requires positive values, and `CountTrailingZeroBits` requires nonzero values. Signed small types need careful casting to avoid sign-extension surprises; the implementation masks where needed. Platform-specific intrinsic branches must stay semantically aligned.

Test signals: `hash_test.cc` exercises these helpers over many signed and unsigned integral types plus `Unsigned128` specializations, checking bit masks, logs, trailing zeros, popcount, parity, endian swaps, reverse bits, downward involution properties, and typed `BitwiseAnd`.
