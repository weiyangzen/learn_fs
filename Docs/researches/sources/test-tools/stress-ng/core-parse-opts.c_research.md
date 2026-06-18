# sources/test-tools/stress-ng/core-parse-opts.c

Purpose: implements typed option parsing, range validation, unit scaling, percentage conversion, method lookup, domain/port parsing, and storage into the settings system.

Important APIs/functions: range checkers, numeric getters, `stress_get_uint64_scale`, byte/time/percentage helpers, `stress_get_int32_instance_percent`, `stress_parse_opt`, and `stress_unimplemented_method`.

Control flow: scalar parsers validate signs/digits, parse with `sscanf`, and on errors print to stderr then `longjmp(g_error_env, 1)`. Byte parsing handles suffixes and cache-size tokens. Percent parsing scales by max and instance count. `stress_parse_opt` switches on `stress_type_id_t`, converts `opt_arg`, checks min/max, and calls `stress_setting_set`; method and callback types use untyped `data`.

State/persistence: writes parsed values into the settings subsystem, relies on global error jump state, and reads CPU/cache/memory/filesystem data for derived values.

Dependencies/integration: `core-parse-opts.h`, settings, CPU cache helpers, network helpers, global `optarg` for one CPU-percent branch, and stress-ng type IDs.

Risks: callers must establish `g_error_env`; suffix multiplication can overflow silently; `TYPE_ID_INT32_CPU_PERCENT` uses global `optarg` instead of local `opt_arg`; filesystem percent helper currently scales against 100; parser exits non-locally.

Test signals: fuzz numeric strings, min/max boundaries, suffixes, cache-size tokens, percent semantics, method choices, callbacks, domain/port parsing, and longjmp recovery.
