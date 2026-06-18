# sources/test-tools/syzkaller/pkg/clangtool/tooltest/tooltest.go

Purpose: Test harness for clangtool-backed packages. It creates per-fixture compile databases, runs a compiled-in clang tool, compares JSON output with golden files, and can load all golden outputs into a merged tool database.

Important APIs/types/functions: `FlagUpdate`, `TestClangTool`, `LoadOutput`, `ForEachTestFile`, `forEachTestFile`, `CompareGoldenFile`, and `CompareGoldenData`.

Control flow: `TestClangTool` skips non-Linux hosts, iterates `testdata/*.c`, writes a temporary `compile_commands.json` with `-DKBUILD_BASENAME`, runs `clangtool.Run`, marshals output, and compares to `<file>.json`. `LoadOutput` reads existing golden JSON for all fixture files, merges and finalizes them with a verifier.

State and persistence behavior: Temporary build dirs hold compile databases and cache files. Golden files are read from the source tree; when `-update` is set, `CompareGoldenData` overwrites the golden file.

Dependencies/integration points: Wraps `pkg/clangtool`, `pkg/osutil`, `pkg/testutil`, `sys/targets`, and `testify/require`. It expects fixture C files under a local `testdata` directory.

Risks: `forEachTestFile` ignores dotfiles and only selects `.c` files, so hidden fixtures need explicit separate tests. `-update` can rewrite goldens, so reviewers need to inspect golden diffs. The harness requires Linux because clang tools are only tested there.

Test signals: Provides reusable golden comparison for `codesearch` and any future clang tool output type implementing `OutputDataPtr`.
