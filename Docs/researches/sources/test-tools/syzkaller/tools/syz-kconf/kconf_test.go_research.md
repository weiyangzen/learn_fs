# sources/test-tools/syzkaller/tools/syz-kconf/kconf_test.go

Purpose: this test file covers low-level parsing helpers used by `syz-kconf`.

Important APIs and flow: `TestReleaseTag` checks `releaseTagImpl` against Makefile snippets for stable `v<major>.<minor>` extraction and a missing-version error. `TestParseNode` unmarshals YAML list entries and checks `parseNode` for bare yes configs, integer values, quoted strings, `n`, list forms with yes/no/int, and constraints.

State and persistence: no files are written; all inputs are inline strings.

Dependencies and integration: uses `kconfig.No`, `yaml.v3`, and Go testing.

Risks: tests do not cover merge/override semantics, feature matching, Kconfig verification, or actual kernel config generation.

Test signals: direct regression signal for the parser primitives most likely to break due to YAML typing/style changes.
