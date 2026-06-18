# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_code.c

This file is the pre-delete-code side of a fixture pair. It defines `func1` with a single marker statement `line1`.

Its only exposed unit is `void func1()`. Control flow has no branches, state, persistence, or external dependencies. The marker is intentionally not valid C syntax because the file is consumed as integration test data, not built.

The paired `commit2/delete_code.c` is empty, so this file tests handling of code removal where a path still exists but contains no source lines. Risks are around line mapping: removed executable markers should not be incorrectly attributed to the empty successor file. The test signal is the stark non-empty-to-empty transition.
