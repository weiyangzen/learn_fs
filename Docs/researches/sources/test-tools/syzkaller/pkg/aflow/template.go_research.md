# sources/test-tools/syzkaller/pkg/aflow/template.go

Purpose: validates and renders text templates used by aflow prompts, with support for crash-title predicates and JSON formatting.

Important APIs/functions: `formatTemplate`, `verifyTemplate`, `walkTemplate`, `parseTemplate`, `templateFuncs`, and `titleIs`. `templateFuncs` includes `titleIsUAF`, `titleIsKASANNullDeref`, `titleIsWarning`, and `jsonMarshal`.

Control flow: `verifyTemplate` parses with `missingkey=error`, walks the parse tree to collect root field names, verifies each used variable is provided, builds zero values for those variables, and executes the template once. `formatTemplate` reparses and executes against runtime state, panicking on errors that should have been caught during verification. `walkTemplate` handles common nodes: lists, if/range/action/pipe/command, fields, variables, chains, literals, identifiers, dot, and reports unsupported parse node types.

State and persistence: no persistence. Runtime input is the template string and state map.

Dependencies and integration: uses Go `text/template` and `parse`, `reflect`, `bytes`, `encoding/json`, `slices`, and syzkaller `pkg/report/crash`. It integrates with agent/action prompt validation and rendering.

Risks and test signals: risks include unsupported template node kinds, only top-level field tracking for chains, panic-on-render if verification was skipped, and function behavior tied to crash title classification. `template_test.go` verifies variable discovery and warning-title rendering.
