# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_dechanyu.c

Read completely: 443 lines.

This module implements DEC Hanyu ctype and stdenc support. It is a mostly tableless 1-, 2-, or 4-byte state machine with a special `HANYUBIT` marker for the Hanyu extension sequence.

Key behavior: bytes `<=0x7F` are single-byte. Lead bytes are `0xA1-0xFE`; trail bytes are `0x21-0x7E` after clearing bit 7. A leading `0xC2 0xCB` sequence marks extended Hanyu data. `mbrtowc_priv` preserves partial input in `_DECHanyuState`; `wcrtomb_priv` emits ASCII, normal two-byte sequences, or four-byte Hanyu sequences. Standard-encoding conversion maps these forms into csid/index planes 0 through 4.

Important interactions: no external tables or variables; exports through ctype/stdenc templates.

Security/reliability notes: state transitions validate each saved byte before continuing. Illegal states return `EINVAL`; malformed sequences return `EILSEQ`; incomplete reads return `(size_t)-2`.
