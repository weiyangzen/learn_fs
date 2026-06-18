# sources/test-tools/fio/parse.c

Purpose: core parser for fio job-file and command-line options.

Important APIs/functions: exported functions include `str_to_float()`, `str_to_decimal()`, `check_str_bytes()`, `check_str_time()`, `strip_blank_front()`, `strip_blank_end()`, `find_option()`/`find_option_c()`, `sort_options()`, `parse_cmd_option()`, `parse_option()`, `string_distance()`, `string_distance_ok()`, `show_cmd_help()`, `fill_default_options()`, `options_init()`, `options_mem_dupe()`, and `options_free()`. Internal helpers handle unit suffixes, value-pair sorting, range display, option help, default validation, and value storage.

Control flow: parsing starts by locating an option through exact/alias matching, splitting `name=value`, and passing the option/value into `handle_option()`. `handle_option()` handles repeated values separated by comma, colon, or dash depending on option type, then calls `__handle_option()` for each segment. The switch in `__handle_option()` validates and stores values by type: strings and enumerations use `posval`, numeric values use byte/time suffix parsing and min/max/power-of-two checks, ranges fill paired offsets, float lists track precision, booleans handle negation, and deprecated/unsupported options report diagnostics. Defaults and profile-specific options reuse the same parser.

State and persistence: global static `__fio_options` is temporarily used during `sort_options()` for priority comparison. Parsed string options allocate and own duplicated strings unless `no_free` is set. Dump-list entries allocate `print_option` nodes for later reporting.

Dependencies and integration: depends on fio option metadata (`struct fio_option`), option categories/groups, logging/debug, arithmetic parser when `CONFIG_ARITHMETIC` is enabled, and helpers from `minmax`, `pow2`, and IEEE float wrappers. It is central to job setup and profile expansion.

Risks: parser behavior is highly metadata-driven; bad offsets, callbacks, or option types can corrupt target option structs. Unit suffix logic is subtle, including percent encoding as negative unsigned values and zone suffix values. `strip_blank_end()` treats `;` and `#` as comments unconditionally. Some conversions rely on `strtoll()`/`sscanf()` edge behavior.

Test signals: option parser tests should cover every `fio_opt_type`, byte/time units including IEC/SI behavior, arithmetic expressions, percentages, zone suffixes, ranges, multi-value replication, validation callbacks, defaults, deprecation, closest-help suggestions, and memory cleanup.
