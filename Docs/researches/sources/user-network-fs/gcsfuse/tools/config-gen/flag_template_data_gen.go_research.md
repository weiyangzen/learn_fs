<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/flag_template_data_gen.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/flag_template_data_gen.go

Purpose: Converts parsed configuration parameter metadata into template data for generating pflag/viper flag declarations and config field bindings.

Important APIs, types, and functions: `flagTemplateData` embeds `Param` and adds `Fn`, `GoPath`, and `GoType`. `computeFlagTemplateData` maps every `Param` through `computeFlagTemplateDataForParam`. `capitalize` converts hyphen-separated names to exported Go identifier segments. `computeFlagTemplateDataForParam` normalizes default values, chooses pflag function names, escapes usage text, computes dotted Go config paths, and maps types through `getGoDataType`.

Control flow: For each parameter, a type switch handles scalar, duration, custom string-like, and slice types. Duration defaults are parsed with `time.ParseDuration` and emitted as nanosecond expressions. Config paths are split by `.`, each segment is capitalized by `-`, and joined back with dots for generated selector paths.

State and persistence behavior: Pure transformation of `Param` values; no file I/O. It mutates only the local copy of `Param` embedded into returned template data.

Dependencies and integration points: Consumed by `main.go` template execution. Depends on type names accepted by `parser.go` and `getGoDataType` from `type_template_data_gen.go`. Integrates with generated `config.go` and `config_test.go` templates.

Risks and test signals: Incorrect default formatting can produce invalid generated Go. `[]int`/`[]string` defaults are inserted inside literal braces without parsing. Duration parse errors are propagated. Test coverage is indirect through config generation tests rather than a dedicated file in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/flag_template_data_gen.go -->
