# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/add_line.c

This tiny C fixture represents the pre-change side of an added-line scenario. It contains a single `func1` body with only `line2`, intentionally using placeholder tokens rather than compilable C statements.

The important API is just `void func1()`. Control flow is linear and empty aside from the marker line. There is no state, persistence, dependencies, or integration logic beyond its path in covermerger integration data.

Its paired `commit2/add_line.c` adds `line3`, so this file helps validate whether covermerger maps coverage and diff hunks when a line is inserted after an existing line. The main risk is treating it as buildable C; it is a structural diff fixture. Test signal is the minimal before/after contrast.
