# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc16.c

Read completely: 213 lines.

This file implements `mbrtoc16` and `mbrtoc16_l`, decoding locale multibyte input into UTF-16 code units. It delegates scalar decoding to `mbrtoc32_l`; BMP scalars are returned directly, while non-BMP scalars are split into a high surrogate returned immediately and a saved low surrogate returned on the next call with `(size_t)-3`.

Important interactions: embeds a `mbrtoc32` state inside `mbstate_t` after a pending-surrogate field, with compile-time layout assertions.

Security/reliability notes: null `s` follows the standard reset behavior. Pending low surrogate delivery consumes no input. Static state for null `ps` is permitted but not race-free.
