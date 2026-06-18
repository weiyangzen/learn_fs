# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_file.c

This fixture models a file that exists in commit1 and is absent from the commit2 list. It contains `func1` with a single marker `line1`.

There are no meaningful runtime APIs beyond the placeholder function, and no state or persistence behavior. Its integration behavior is entirely path-level: covermerger must recognize a source file that disappears between revisions.

The risk is conflating deleted-file handling with empty-file handling. Unlike `delete_code.c`, there is no mapped commit2 counterpart in this work item. Test signal is the presence-only-in-commit1 path, which validates deletion accounting and prevents stale coverage from being assigned to unrelated files.
