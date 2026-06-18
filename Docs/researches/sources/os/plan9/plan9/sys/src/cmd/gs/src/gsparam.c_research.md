# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.c

Implements core parameter-list helpers for Ghostscript’s typed key/value parameter dictionaries.

Key functions:
- GC relocation/enumeration for `gs_param_typed_value`.
- `gs_param_list_init`: initializes common list procedure table, allocator, and persistent-key default.
- `gs_param_list_set_persistent_keys`: toggles key lifetime contract.
- `param_init_enumerator`: zeroes enumerator state.
- `gs_param_read_items` / `gs_param_write_items`: transfer structured fields based on `gs_param_item_t` descriptors.
- `param_coerce_typed`: supports selected coercions among int/long/float, string/name, string/name arrays, int array to float array, and empty array to typed arrays.
- `param_read_requested_typed`, fixed-type readers, and fixed-type writers.
- Defaults: `gs_param_request_default`, `gs_param_requested_default`.

Integration:
- Implements interfaces declared in `gsparam.h`.
- Used broadly by device `get_params` / `put_params` and incremental parameter list construction.

Risk notes:
- `param_coerce_typed`’s int-to-float case assigns from `value.l` after actual type `int`; this looks suspicious because `value.l` may not be initialized as a long.
- `param_read_name` requests `gs_param_type_string` while returning union member `n`; this may be deliberate compatibility or a typo.
- Error accumulation in item reads/writes keeps scanning after failures, matching device parameter policy but requiring callers to inspect final code.
