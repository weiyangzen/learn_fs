# File Research: sources/virtualization/spdk/lib/util/cpuset.c

This file implements fixed-size SPDK CPU-set allocation, mutation, formatting, iteration, and parsing.

Basic operations allocate/free sets, compare, copy, negate, bitwise and/or/xor, zero, set/get individual CPUs, iterate set CPUs, and count CPUs. CPU index setters/getters assert the index is within the fixed `cpus` byte array.

`spdk_cpuset_fmt()` formats the bitmask as a compact lowercase hexadecimal string without leading zero high nibbles, writing into the set’s internal `str` buffer. It scans for the highest set CPU and formats bytes from high to low.

Parsing supports two formats. Hex masks may have optional `0x`/`0X` prefix and may contain comma delimiters like Linux cpumasks; parsing walks the string right-to-left and maps hex nibbles to CPU bits. List masks start with `[` and support comma-separated CPU numbers and ranges with optional blanks, such as `[0,2-4]`; invalid syntax, out-of-range CPUs, reversed ranges, and conversion errors are logged and rejected.

Important invariants are fixed `SPDK_CPUSET_SIZE`, internal formatting buffer ownership, and strict parse rejection. List parsing stops at `]` and does not require trailing text validation beyond that point as read, so callers should pass clean mask strings.
