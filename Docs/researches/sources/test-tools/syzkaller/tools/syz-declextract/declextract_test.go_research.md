# sources/test-tools/syzkaller/tools/syz-declextract/declextract_test.go

Purpose: this file provides regression tests for the clang extraction wrapper and end-to-end description generation from synthetic kernel fixture files.

Important APIs and flow: `TestClangTool` delegates to `tooltest.TestClangTool` for `clangtoolimpl.Tool`. `TestDeclextract` iterates all clang-tool fixture C files, symlinks the corresponding `.json` golden into the clang cache to avoid invoking the real extractor, symlinks `manual.txt`, stubs `cfg.Tool`, loads optional `.probe` and `.cover` fixtures, and calls `run`. It then parses all generated descriptions, extracts constants, fabricates constant values, compiles the descriptions, checks generated type size/alignment against `res.StructInfo`, and compares `autoFile` plus `.info` to golden files. With update mode it copies generated output back to goldens on failure.

State and persistence: the test writes symlinks and generated auto files into the temporary kernel object directory prepared by `tooltest`. It reads fixture JSON, optional probe/coverage files, manual descriptions, and golden text/info outputs.

Dependencies and integration: uses `pkg/clangtool/tooltest`, `pkg/compiler`, `pkg/ast`, `pkg/ifaceprobe`, `pkg/osutil`, and the real `run` function. It checks the integration boundary between cached clang JSON and generated syzkaller DSL.

Risks: because the clang tool is replaced by a cache symlink, these tests emphasize downstream processing rather than live clang invocation. The TODO notes missing coverage for whether generated syscalls survive `TransitivelyEnabledCalls`.

Test signals: strong signal for fixture-level semantics, struct layout parity, compiler acceptance, and formatting/golden stability.
