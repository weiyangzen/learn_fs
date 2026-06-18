<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser_test.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/parser_test.go

Purpose: Unit tests for params YAML parsing and validation in the config generator.

Important APIs, types, and functions: Tests cover `checkFlagName`, `validateMachineTypeGroups`, `validateForDuplicatesInSortedSlice`, and `parseParamsYAMLStr`. Positive parsing asserts machine groups and optimization rules for bucket-based, machine-based, profile, mixed, and absent optimization cases. Negative parsing checks malformed YAML, duplicate flag names, invalid group name, unsorted/duplicate/empty machine groups, and unsupported bucket type.

Control flow: Table-driven tests call validation helpers and assert errors or substrings. The success YAML fixture includes sorted config paths and machine groups, then subtests inspect parsed `Param.Optimizations`.

State and persistence behavior: No file I/O; YAML content is embedded strings. Tests do not mutate global flags.

Dependencies and integration points: Depends on `cfg/shared`, `testify/assert`, and `testify/require`. It provides schema-safety signal for generator input consumed by `main.go`.

Risks and test signals: Strong coverage of machine group validation and optimization parsing. Gaps include no test for param sorting failures in the visible subset, no duplicate config-path case, and no unknown-field assertion despite `KnownFields(true)`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/parser_test.go -->
