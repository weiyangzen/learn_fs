# sources/test-tools/syzkaller/tools/syz-kconf/parser.go

Purpose: this file parses `syz-kconf` YAML specs into `Instance` objects with kernel, compiler, shell, features, verbatim text, and config entries.

Important APIs and flow: data types include `Instance`, `Config`, `Kernel`, `Shell`, and `Features`. `Features.Match` evaluates positive and negative constraints. `parseMainSpec` reads the main YAML, preserves unused feature declarations under `_`, creates normal and `-base` instances with baseline/base-config features, and expands includes. `parseInstance` initializes features, reads included bit files, merges matching fragments, and for reduced instances turns excluded non-reduced yes/no configs into weak disables. `mergeFile` sets singleton kernel/compiler/linker fields, prepends shell commands, appends verbatim blocks, and merges configs. `mergeConfig` parses a YAML node, handles `override`, `optional`, `weak`, and `append`, detects duplicates, appends quoted string values, and records file/line metadata. `parseNode` supports bare names, scalar int/string/no values, and list syntax mixing value and constraints. `Errors` accumulates formatted messages.

State and persistence: reads YAML files only and returns in-memory instances. File and line metadata are preserved for diagnostics.

Dependencies and integration: uses `pkg/kconfig`, `pkg/vcs` validation helpers, `yaml.v3`, slices, and filesystem reads. Consumed by `kconf.go`.

Risks: map iteration over one-key YAML maps takes the first entry; malformed multi-key nodes are not explicitly rejected. Append requires quoted strings. Override without existing non-optional config is an error. Reduced-mode inversion only applies to yes/no values.

Test signals: `kconf_test.go` covers `parseNode`; broader merge behavior currently relies on integration use.
