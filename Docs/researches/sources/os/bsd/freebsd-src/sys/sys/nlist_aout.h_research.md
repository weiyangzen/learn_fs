# File Research: sources/os/bsd/freebsd-src/sys/sys/nlist_aout.h

This header defines legacy a.out symbol table entries and associated constants. `struct nlist` represents one symbol, with conditional layout support for `_AOUT_INCLUDE_`: the name field can be a memory pointer or an on-disk string-table offset union, otherwise it is exposed as a pointer for consumers of `nlist.h`.

The fields record symbol type, auxiliary/binding bits, stab description, and value/address. Constants define classic a.out symbol classes such as undefined, absolute, text, data, BSS, indirect, common, GNU set symbols, file/warning entries, external bit, type mask, and debugger/stab mask. Helper macros extract/pack the low-nibble auxiliary field and high-nibble binding field from `n_other`, with definitions for object/function auxiliary types and weak binding.

Filesystem relevance is historical/tooling oriented: this is not part of runtime VFS, but it defines on-disk executable symbol metadata understood by older tools and compatibility code.
