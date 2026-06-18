# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/change_line.c

This is the post-change side of a modified-line fixture. `func1` contains `line2_changed` followed by unchanged `line3`.

There are no runtime APIs beyond the placeholder function, no state, and no dependencies. Control flow is flat; the changed marker is the whole purpose of the file.

The file integrates with the paired commit1 fixture to verify changed-line detection. It should let covermerger distinguish a replacement line from stable surrounding context. The risk is false continuity: tools must not treat `line2_changed` as the same source line as `line2` except as a diff-mapped modification.
