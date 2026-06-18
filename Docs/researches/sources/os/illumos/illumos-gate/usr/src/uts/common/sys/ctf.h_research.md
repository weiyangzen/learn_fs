# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf.h

On-disk/in-memory format definition for Compact ANSI-C Type Format data. It describes the CTF section layout, header, type records, labels, string references, type kind encoding, integer/float encodings, arrays, members, large members, and enums.

Key elements:
- Opening comment documents the CTF file layout: header, labels, object types, function info, data types, and string table.
- Defines maximum type ID, name offset, variable-length member count, integer offset/bits, normal type size, large-size sentinel, and maximum large size.
- `ctf_preamble_t` and `ctf_header_t` encode magic/version/flags and section offsets relative to the end of the header.
- Optional `CTF_OLD_VERSIONS` block defines the older v1 header and v1 info packing macros.
- Defines CTF magic, supported/current versions, and compression flag.
- `ctf_lblent_t` maps a label string reference to the last type ID covered by that label.
- `ctf_stype_t` is the compact type record for normal-size types; `ctf_type_t` extends it with 64-bit size split into high/low words.
- Macros pack and unpack `ctt_info` kind/root/vlen fields and `ctt_name` string-table/id offsets.
- Parent/child type-id macros split type IDs around `CTF_CHILD_START` and convert between IDs and indexes.
- Defines string table IDs 0 and 1, large-size helpers, and large-member offset helpers.
- Enumerates CTF type kinds: unknown, integer, float, pointer, array, function, struct, union, enum, forward, typedef, volatile, const, and restrict.
- Defines integer and floating-point encoding macros and flags, including signed/char/bool/varargs and many float encodings.
- Defines `ctf_array_t`, `ctf_member_t`, `ctf_lmember_t`, and `ctf_enum_t`.

Dependencies:
- Uses fixed-width and system integer types from `sys/types.h`.
- Consumed by libctf, kernel CTF support, debuggers, CTF tools, and code that reads `.SUNW_ctf` ELF sections.

Research notes:
- The format is data-model independent and designed for mmap-friendly parsing; structures avoid native pointer-sized fields.
- Struct/union member encoding switches to `ctf_lmember_t` when the containing type size reaches `CTF_LSTRUCT_THRESH`.
- String references deliberately support both internal CTF strings and the external ELF string table to avoid duplication.
