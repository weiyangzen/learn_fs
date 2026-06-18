# sources/test-tools/syzkaller/pkg/aflow/template_test.go

Purpose: tests template variable discovery, validation errors, and custom template functions.

Important APIs/functions: `TestTemplate` drives `verifyTemplate` with text-only templates, conditionals, local variables, ranges, missing variables, builtin functions, chains, parenthesized chains, and comparisons. `TestTemplateRender` executes `parseTemplate` with crash-title predicate functions.

Control flow: each `TestTemplate` case supplies a template, available variable types, expected used roots, or an error. It asserts used variables with `ElementsMatch`, so order is irrelevant. Render testing checks that only `titleIsWarning` matches a warning title.

State and persistence: no persistence; all data is local maps and buffers.

Dependencies and integration: imports `bytes`, `fmt`, `maps`, `reflect`, `slices`, `testing`, and testify. It directly validates `template.go`, which is used by LLM prompt and instruction formatting.

Risks and test signals: good coverage exists for common parse nodes, but unsupported template constructs remain a risk because `walkTemplate` intentionally handles only a practical subset. The rendering test detects regressions in crash-title classification wiring.
