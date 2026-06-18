# File Research: sources/os/bsd/freebsd-src/sys/sys/ctf.h

## Purpose
Defines the Compact C Type Format ABI structures and macros for CTF v2/v3 data embedded in ELF files.

## Main Elements
- Header structures: `ctf_preamble_t`, `ctf_header_t`, compression flag.
- Type records for v2/v3 short and long types, arrays, members, large members, labels, and enums.
- Magic/version constants with current `CTF_VERSION_3`.
- v2/v3 limits for vlen, size, large-size sentinel, type IDs, and parent/child encoding.
- Macros pack/unpack type info, names, integer/float encodings, large type sizes, and large member offsets.
- Defines CTF kind values for integer, float, pointer, array, function, struct, union, enum, forward, typedef, and qualifiers.
- Compatibility typedefs and macros map unsuffixed names to v2.

## Dependencies And Integration
Used by CTF generation/loading code and kernel linker CTF support. Includes `sys/_types.h`.

## Risk Notes
This is a binary format contract. Version-specific field widths and ID encodings must be matched by parsers, generators, and debugger consumers.
