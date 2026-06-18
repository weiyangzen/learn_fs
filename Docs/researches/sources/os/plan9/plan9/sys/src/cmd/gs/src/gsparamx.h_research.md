# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.h

Declares extended parameter dictionary utilities.

Exports:
- `gs_param_string_eq`
- `param_put_enum`
- `param_put_bool`
- `param_put_int`
- `param_put_long`
- `param_list_copy`

Integration:
- Requires parameter-list types from `gsparam.h` to be visible.
- Designed as convenience support for robust `put_params` parsing and list duplication.

Risk notes:
- Thin declarations only; error accumulation semantics are defined by implementations in `gsparamx.c`.
