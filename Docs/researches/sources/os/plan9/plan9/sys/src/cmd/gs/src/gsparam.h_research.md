# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.h

Defines Ghostscript’s generic parameter dictionary abstraction.

Key definitions:
- `gs_param_type`: scalar, homogeneous collection, and heterogeneous collection type IDs.
- Homogeneous array/string structs: `gs_param_int_array`, `gs_param_float_array`, `gs_param_string_array`.
- `gs_param_collection`, `gs_param_dict`, `gs_param_array`.
- `gs_param_value`, `gs_param_typed_value`, and GC procedures for typed values.
- `gs_param_collection_type_t`: general dict, int-key dict, or array.
- `gs_param_list_procs`: virtual table for typed transmission, begin/end collection, key enumeration, requests, policies, error signaling, and commit.
- Helper macros for reading/writing, begin/end dict, request/query, policy, signal, and commit.
- `gs_param_list` common base with proc table, allocator, and persistent-key flag.
- `gs_param_item_t` descriptor-based transfer API.
- `gs_c_param_list`: C-side default/incremental parameter list with optional forwarding target.

Integration:
- Core contract for device parameter exchange and PostScript-like dictionaries.
- The header embeds detailed two-phase `put_params` policy guidance for device implementers.

Risk notes:
- The API deliberately reuses one procedure table for “reading” and “writing” from opposite client/device perspectives, which is powerful but easy to misuse.
- Persistent vs transient key/value ownership is central; callers must set flags consistently.
