## sources/test-tools/syzkaller/pkg/kconfig/fuzz.go

Purpose: exposes fuzz targets for Kconfig file parsing, `.config` parsing, and expression parsing.

Important APIs/types/functions: `FuzzParseKConfig`, `FuzzParseConfig`, `FuzzParseExpr`, and `init`.

Control flow: fuzz functions call parse routines with arbitrary data and return `1` to keep corpus entries. `init` likely wires syzkaller/pkg fuzz helpers or seeds parser behavior.

State and persistence: no persistent state.

Dependencies and integration: integrates Go fuzzing with the Kconfig parser stack and target metadata.

Risks: fuzz targets validate robustness, not semantic output. If they swallow all errors, they can miss incorrect successful parses.

Test signals: `kconfig_test.go` and `expr_test.go` invoke fuzz entry points on fixed data.
