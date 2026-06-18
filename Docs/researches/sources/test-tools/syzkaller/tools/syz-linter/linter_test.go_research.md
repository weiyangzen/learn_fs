# sources/test-tools/syzkaller/tools/syz-linter/linter_test.go

Purpose: this test wires the custom analyzer into Go's analysistest framework.

Important APIs and flow: `TestLinter` calls `analysistest.Run(t, osutil.Abs("testdata"), SyzAnalyzer, "lintertest")`, which compiles fixture packages under `testdata/src` and checks `// want` diagnostics.

State and persistence: read-only testdata use; no writes.

Dependencies and integration: depends on `pkg/osutil.Abs`, `golang.org/x/tools/go/analysis/analysistest`, and the `SyzAnalyzer` symbol.

Risks: this only runs the custom analyzer, not the full `New` analyzer bundle. Coverage depends on the unlisted `lintertest` fixture contents.

Test signals: primary direct regression signal for custom linter diagnostics and fixture import resolution.
