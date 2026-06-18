# sources/test-tools/syzkaller/tools/syz-linter/linter.go

Purpose: `syz-linter` is syzkaller's custom Go analyzer plugin, bundling project-specific style/bug checks with selected standard analyzers and the modernize suite.

Important APIs and flow: `New` returns `SyzAnalyzer` plus analyzers for atomic alignment, copylocks, deep-equal errors, nilness, struct tags, waitgroups, HTTP response handling, and modernize. `run` walks each AST file, tracks statement lines, dispatches node-specific checks, then checks comments and top-level declaration spacing. Custom checks include comment format and punctuation, string `len` comparisons to zero, grouped function args, context argument position/name, flag naming/descriptions, manual slice clone, log/error message capitalization/newline/period rules, redundant var declarations with type and value, min/max if statements, loop variable self-assignment, `interface{}` to `any`, sort API modernization, range-over-int loop modernization, while-style loop scoping, manual map-key extraction followed by sort, `strings.Index` plus slicing, and multi-line struct literals with multiple fields per line.

State and persistence: analyzer-only; no writes. It reports diagnostics through `analysis.Pass`.

Dependencies and integration: uses Go AST/types/printer/token packages and `golang.org/x/tools/go/analysis`. It is intended for golangci-lint plugin use; `main` keeps `New` reachable.

Risks: many checks are heuristic and can produce false positives, especially string/log formatting, sort modernization, and strings.Index slicing. `fmt.Sprintf("%v.%v", fun.X, fun.Sel)` is syntax-string based, not full object resolution. Type info must be available for several checks. Some modern Go version assumptions are embedded, e.g. loop variables since Go 1.22.

Test signals: `linter_test.go` runs `analysistest` over fixture package `lintertest`; the assigned `pkg/tool/tool.go` stub supports expected diagnostics involving `tool.Fail*`.
