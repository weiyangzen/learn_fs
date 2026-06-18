<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/main.go

Purpose: Entry point for generating gcsfuse config Go source and tests from a params YAML file plus text templates.

Important APIs, types, and functions: Flags `-outDir`, `-paramsFile`, and `-templateDir` configure generation. `templateData` carries type template data, flag template data, machine type maps/groups, and a `Backticks` string for templates. `validateFlags`, `write`, `invertMachineTypeGroups`, `formatValue`, and `main` orchestrate parsing and rendering.

Control flow: `main` parses flags, validates required paths, parses params YAML, constructs type and flag template data, sorts both deterministically, inverts machine group mappings, and renders `config.tpl` and `config_test.tpl` to `config.go` and `config_test.go`. `write` creates output files and executes templates with `formatValue` and title-casing helpers.

State and persistence behavior: Writes generated files directly with `os.Create`, truncating existing outputs. It panics on validation, parse, or generation errors. No atomic write is used.

Dependencies and integration points: Depends on local parser/type/flag helpers, `cfg/shared` optimization types, Go `text/template`, `golang.org/x/text/cases`, and template files. Generated outputs are part of the gcsfuse config package contract.

Risks and test signals: `invertMachineTypeGroups` panics on duplicate machine mapping; parser validation also rejects duplicates, so panic is a defensive layer. `formatValue` treats exported strings ending in `()` as function calls, which is powerful but could misclassify values. Tests cover machine group inversion and duplicate panic behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/main.go -->
