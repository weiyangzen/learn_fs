# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_big5.c

Read completely: 514 lines.

This module implements BIG5 ctype and stdenc support. It keeps a 256-entry cell table marking legal lead rows and trailing columns, plus a sorted list of excluded code ranges parsed from optional module variables.

Key behavior: `row` and `col` numeric property ranges set lead/trail byte classes; `excludes` ranges reject otherwise valid code points. If variable parsing is absent or fails, it falls back to Big5-1984 defaults: rows `0xA1-0xFE`, columns `0x40-0x7E` and `0xA1-0xFE`. `mbrtowc_priv` buffers up to 2 bytes and returns restart/error statuses; `wcrtomb_priv` validates width, row/column, and exclusions before writing.

Important interactions: uses `citrus_prop` for variable parsing and shared ctype/stdenc templates for exported APIs.

Security/reliability notes: excludes are appended in increasing non-overlapping order; invalid ranges return `EINVAL`. Conversion resets partial state on illegal sequences. Fallback-on-parse-failure is compatibility-oriented but means malformed variables do not necessarily fail module initialization.
