# sources/test-tools/syzkaller/tools/syz-linter/testdata/src/lintertest/lintertest.go

## Purpose
This file is analyzer testdata for `tools/syz-linter`. It deliberately mixes accepted idioms and lines annotated with `// want "..."` diagnostics so Go analysis tests can verify linter rules against concrete source constructs.

## Important APIs, types, and functions
- Package `lintertest` imports standard packages plus `pkg/tool` only to exercise analyzer recognition of real APIs.
- `stringComparison`, `flagDefinitions`, `logErrorMessages`, `testMessages`, `varDecls`, `minmax`, `loopvar`, `anyInterface`, `contextArgs*`, `sliceClones`, `sortUsage`, `rangeOverIntegers`, `whileStyleLoops`, `mapKeysExtraction`, `stringsCut`, and declaration-spacing examples are fixtures rather than reusable APIs.
- `Foo`, `MissingEmptyLineStruct`, grouped types, and `StructLayout` provide type references for argument grouping and struct literal layout checks.

## Control flow
Execution is unimportant; the linter test runner parses the file and compares emitted diagnostics against `want` comments. Functions include trivial branches, loops, and calls only to trigger AST patterns such as `len(str)==0`, manual min/max updates, duplicated range variables, integer `for` loops, and manual key extraction plus sorting.

## State and persistence behavior
No persistent state is created. Local variables and maps exist only to make syntactically valid examples. The file's durable state is the source text itself: diagnostic comments are the assertion data consumed by analyzer tests.

## Dependencies and integration points
The file integrates with Go analysis test harness conventions where `// want` marks expected messages. Imports of `flag`, `fmt`, `log`, `sort`, `strings`, `testing`, `context`, and `tool` intentionally create call sites for specific syzkaller linter rules.

## Risks and edge cases
Because this is negative testdata, many lines intentionally violate repository style and should not be mechanically formatted into "better" code. Changes to diagnostic wording or Go version idioms can break tests even when behavior is unchanged. Several examples rely on subtle syntactic shape, such as grouped single-line functions, multi-line struct literals, and `sort.Slice` predicate patterns.

## Test signals
Strong direct test signal: each `want` comment states an expected analyzer diagnostic. The file covers both positive and negative cases for comments, logging, flag naming, context argument placement, modern library replacements, declaration spacing, and struct literal layout.
