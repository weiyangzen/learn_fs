# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.h

Declares extended parameter dictionary helpers from `gsparamx.c`.

Exports:
- `gs_param_string_eq`
- `param_put_enum`
- `param_put_bool`
- `param_put_int`
- `param_put_long`
- `param_list_copy`

The helpers are convenience wrappers around `gs_param_list` operations, especially for device-style parameter ingestion with accumulated error handling.
