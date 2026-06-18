# sources/test-tools/crashmonkey/code/results/PermuteTestResult.h

Purpose: declares the logged description of a generated crash state.

Important APIs/types: stores `last_checkpoint` and `std::vector<DiskWriteData> crash_state`; exposes printers for size and tuple list.

Control flow and integration: permuters populate it, `Tester` passes it through `SingleTestInfo`, and result logs record it.

State and persistence behavior: state is in-memory during a run and persisted only through text logs.

Risks: `last_checkpoint` is not default-initialized in the header, so generators must always set it before printing. The vector can be large for many-sector states.

Test signals: default construction followed by printing should be avoided or tested for initialization issues.
