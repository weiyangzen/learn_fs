# sources/test-tools/syzkaller/executor/style_test.go

Purpose: Go style/regression test enforcing executor source patterns that affect csource generation, reproducibility, and runtime safety.

Important APIs and control flow: `TestExecutorMistakes` defines regex checks with optional suppressions, example snippets that must match, and `commonOnly`/`fuzzerOnly` filters. It scans all `*.cc` and `*.h` files from `executorFiles`, reports line-local errors, and excludes runner helper files from allocation restrictions. `executorFiles` globs C++ and header files, requires both classes to exist, concatenates and sorts them.

State and dependencies: test-only state is the checks table. Depends on Go `testing`, regex, bytes, filepath globs, slices, and strings.

Integration points: protects assumptions in `embed.go` and executor design: debug calls in common headers need braces for csource stripping, block comments are banned, `SYZ_*` macros should use `#if`, malloc/new are discouraged in fuzzer paths, and exit APIs should go through executor wrappers.

Risks and tests: regex checks can have false positives/negatives, so suppressions are part of the contract. The test is itself the direct signal and should run in Go package tests for the executor.
