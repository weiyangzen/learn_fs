# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc8.c

Read completely: 226 lines.

This file implements `mbrtoc8` and `mbrtoc8_l`, decoding locale multibyte input into UTF-8 code units. It delegates scalar decoding to `mbrtoc32_l`, returns the first UTF-8 byte immediately, and buffers up to three trailing bytes for later `(size_t)-3` returns without consuming input.

Important interactions: embeds `mbrtoc32` state after UTF-8 output buffering in `mbstate_t`, with compile-time size/alignment assertions.

Security/reliability notes: rejects scalar values outside Unicode's UTF-8 range with `EILSEQ`. Pending trailing bytes are cleared as they are emitted. Static state for null `ps` is not race-free by standard allowance.
