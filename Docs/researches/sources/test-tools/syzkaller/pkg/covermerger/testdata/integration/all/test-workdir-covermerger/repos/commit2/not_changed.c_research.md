# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/not_changed.c

This is the commit2 side of the unchanged-file fixture. It defines the same placeholder `func1` body with `line1`, `line2`, and `line3`.

No functional APIs, persistence, dependencies, or state are present. The only meaningful control-flow fact is that the source layout remains identical to commit1.

Its integration value is stable baseline coverage mapping. Covermerger should preserve line correspondence exactly despite the different commit directory. Test signal is byte-level sameness with `commit1/not_changed.c`; risk is any path-only logic that reports a change where none exists.
