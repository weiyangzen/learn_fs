# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idictdef.h

Internal dictionary representation details. It documents dictionary capacity semantics, packed vs unpacked key arrays, deleted/empty markers, and the wraparound sentinel entry.

Defines:
- `dict_is_packed`
- packed key constants
- `packed_name_key`
- length/capacity/slot macros
- `packed_search_1` and `packed_search_2` probing macros

This file is implementation-private but shared with high-performance dictionary stack lookup.
