# sources/test-tools/syzkaller/tools/syz-linter/testdata/src/github.com/google/syzkaller/pkg/tool/tool.go

Purpose: this tiny test fixture provides a stub `github.com/google/syzkaller/pkg/tool` package for linter analysistest imports.

Important APIs and flow: package `tool` defines no-op `Failf(msg string, args ...interface{})` and `Fail(err error)` functions.

State and persistence: none.

Dependencies and integration: imported by linter test packages that need `tool.Failf`/`tool.Fail` symbols without depending on the real syzkaller package.

Risks: signatures must stay compatible with fixture expectations. The use of `interface{}` may itself be intentional testdata and should not be updated casually.

Test signals: successful fixture compilation during `analysistest.Run` confirms this stub is sufficient.
