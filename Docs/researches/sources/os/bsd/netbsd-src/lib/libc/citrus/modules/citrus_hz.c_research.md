# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_hz.c

Read completely: 728 lines.

This module implements configurable HZ ctype and stdenc support. HZ is state-dependent: escape sequences switch active GL/GR graphic sets, and character interpretation depends on the active escape entry.

Key structures: `graphic_t` records charset, row/column length, and owning escape; `escape_t` links an escape character to GL/GR graphics and its escape set; `_HZEncodingInfo` owns two escape lists plus selected ASCII/GB2312 graphics; `_HZState` stores partial bytes and the active escape.

Key behavior: module variables are parsed with `citrus_prop`, defining escape set `0` and `1` entries with `CH`, `GL`, and `GR` properties. `mbrtowc_priv` handles `~` escapes, line continuation, GL/GR selection, active-set switching, and row/column range validation. `wcrtomb_priv` selects or switches the active escape before output. `put_state_reset` emits a reset escape to the initial set when needed.

Important interactions: uses `citrus_prop` callbacks to allocate escape and graphic nodes; exports through ctype/stdenc templates.

Security/reliability notes: parser-owned allocations are freed by `_citrus_HZ_encoding_module_uninit`. The module is sensitive to malformed variable strings because missing initial escapes can leave `INIT0(ei)` null and later state initialization asserts/depends on it. Conversion functions return `EINVAL` for impossible internal state and `EILSEQ` for invalid byte sequences.
