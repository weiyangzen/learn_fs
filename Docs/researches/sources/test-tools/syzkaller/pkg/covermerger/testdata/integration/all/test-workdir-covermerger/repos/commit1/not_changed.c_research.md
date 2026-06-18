# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/not_changed.c

This is the commit1 side of an unchanged-file fixture. `func1` contains marker lines `line1`, `line2`, and `line3`.

There are no real APIs, control branches, state, persistence, or dependencies. The source is intentionally minimal to isolate path and line preservation behavior.

Its paired `commit2/not_changed.c` is identical, so the integration point is covermerger's unchanged-file reconciliation path. The expected signal is stable line identity across commits. Risk lies in over-attributing differences due to repository directory changes rather than source content changes.
