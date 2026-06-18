# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inames.h

Public name table interface independent of implementation details or a singleton instance.

Key behavior:
- Defines/forwards `name_table` and `name_index_t`.
- Declares `name_max_string`.
- Declares initialization, allocator lookup, and name lookup/entry APIs.
- `names_ref` supports enter modes for no-enter, static string, copied string, or dynamically allocated string ownership.
- Declares conversion helpers: string ref, C-string entry, string-to-name conversion, index-to-ref/name, and next-valid-index traversal.
- Provides `names_eq` as pointer equality on `value.pname`.
- Declares GC support: mark by index and locate the sub-table objects for refs, indices, and strings.
- Declares `names_invalidate_value_cache`.

Research notes:
- This header is intentionally API-level; inline internals live in `inamedef.h`.
- Name equality is identity-based, relying on interning.
