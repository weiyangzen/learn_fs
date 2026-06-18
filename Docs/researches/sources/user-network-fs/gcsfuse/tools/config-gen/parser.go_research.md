<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/parser.go

Purpose: YAML parser and validator for config generator params, including flag metadata, config paths, data types, deprecation settings, optimization rules, and machine type groups.

Important APIs, types, and functions: `Param` models individual params; `ParamsYAML` models top-level YAML. `parseParamsYAMLStr` uses `yaml.Decoder.KnownFields(true)`, then validates params and machine groups. Validation helpers include `checkFlagName`, `validateParam`, `isSorted`, `validateParams`, `validateForDuplicates`, `validateMachineTypeGroups`, and `validateForDuplicatesInSortedSlice`.

Control flow: YAML decoding rejects unknown fields. Param validation enforces sorted order, unique flag names/config paths, valid flag naming, deprecation warnings, required usage/type/config-path for non-deprecated params, supported data types, and valid bucket optimization types. Machine type group validation enforces kebab-case group names, non-empty sorted unique machine lists, and cross-group machine uniqueness.

State and persistence behavior: `parseParamsYAML` reads the file path held in global flag `paramsFile`; `parseParamsYAMLStr` is pure. No output files are written here.

Dependencies and integration points: Depends on `gopkg.in/yaml.v3`, `cfg/shared.OptimizationRules`, and generator code that consumes `ParamsYAML`. It is the schema gate for generated config source.

Risks and test signals: Sorting logic treats params with empty config paths specially for deprecated flags and can reject valid-looking reorderings. `checkFlagName` allows underscores despite comments saying hyphen-separated lower-case. Machine group map key order cannot be sorted-validated because Go maps lose order. Tests cover positive parsing, malformed YAML, duplicate fields, group validation, and invalid bucket types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser.go -->
