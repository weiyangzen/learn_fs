# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/add_line.c

This is the post-change side of the add-line fixture. `func1` contains `line2` and a newly present `line3`.

The file has no functional dependencies, persistence, or state. Its control flow remains a single function body; the important behavior is textual position and line identity relative to commit1.

The integration point is covermerger's added-line mapping. Compared with `commit1/add_line.c`, this file tests whether new coverage lines can be recognized as introduced source while preserving existing-line correspondence. Risk is limited to fixture interpretation: it is not valid buildable C and should be treated as synthetic source data.
