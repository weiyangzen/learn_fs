# sources/test-tools/stress-ng/core-parse-opts.h

Purpose: public typed option parsing contract for stressor-specific options.

Important APIs/types: `stress_opt_t`, `END_OPT`, `stress_scale_t`, declarations for scalar parsers, range checkers, scaling helpers, and `stress_parse_opt`.

Control flow: no header flow; option tables terminate with `END_OPT` and are interpreted by `stress_parse_opt`.

State/persistence: no header state; parsed results are persisted in settings by implementation functions.

Dependencies/integration: includes `core-attribute.h` and `core-setting.h`, and uses `stress_type_id_t` plus standard integer types.

Risks: descriptor `data` is untyped and must match `type_id`; min/max are unsigned even for signed types; `END_OPT` must remain in sync with parser sentinel logic.

Test signals: compile stressor option tables, static sentinel checks, and parser tests for every `TYPE_ID_*` used by stressors.
