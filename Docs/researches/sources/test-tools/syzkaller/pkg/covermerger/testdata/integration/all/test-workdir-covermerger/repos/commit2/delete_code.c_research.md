# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/delete_code.c

This file is intentionally empty. It is the post-change counterpart to a commit1 file that contained a placeholder `func1` body.

There are no APIs, functions, control flow, state, persistence, dependencies, or local tests inside the file. Its meaning comes from the path and empty content in the covermerger integration fixture.

The integration point is deletion-with-path-retained handling. It verifies that an empty successor file is distinct from a missing file and that previous coverage lines are not silently carried forward. The main risk is treating zero-byte research targets as missing; the correct output still needs to document the intentional empty state.
