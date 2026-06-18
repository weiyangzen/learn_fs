# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/change_line.c

This fixture is the pre-change side of a line-modification case. `func1` contains `line2` followed by `line3`, with both lines serving as stable textual markers.

There are no real APIs beyond `func1`, and no runtime state, persistence, or external dependency. Control flow is a simple function body whose second logical line is the target for comparison with `commit2/change_line.c`.

The integration point is the covermerger test fixture set. In the paired commit, `line2` changes to `line2_changed` while `line3` remains stable, letting the merger distinguish changed-line coverage from unchanged-context coverage. The main risk is assuming semantic C behavior; this file is for textual and coverage reconciliation behavior.
