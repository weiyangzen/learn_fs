# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.c

Implements generic support for Ghostscript parameter lists: typed values, value coercion, default scalar/array readers and writers, item-transfer helpers, and default request behavior.

Main behavior:
- Provides GC enumeration/relocation for `gs_param_typed_value`.
- Initializes `gs_param_list` common fields.
- Implements `gs_param_read_items` and `gs_param_write_items` for table-driven structure transfer.
- Implements `param_coerce_typed`, including int/long/float coercions, string/name interchange, and int-array to float-array conversion when memory is available.
- Provides fixed-type read/write wrappers for null, bool, int, long, float, strings, names, and arrays.

Notable detail:
- Missing params convention follows `1` for absent, `0` for present, negative for error.
- `param_read_name` requests `gs_param_type_string` while returning through the name union field; string/name share representation, but this is worth remembering when tracing type behavior.
