## sources/distributed-fs/tahoe-lafs/integration/test_aaa_aardvark.py

Purpose: intentionally early integration smoke tests that instantiate expensive session fixtures and print progress.

Important tests: `test_create_flogger`, `test_create_introducer`, and `test_create_storage`.

Control flow: each test depends on one fixture (`flog_gatherer`, `introducer`, or `storage_nodes`) and prints a short confirmation. The filename sorts early so prerequisite startup happens before more substantive tests.

State and dependencies: triggers creation of flog gatherer, introducer, and storage nodes through `conftest.py`/`grid.py`. It does not add additional persistent state beyond fixture side effects.

Risks and signals: skipping these tests is safe but shifts startup cost to the first later test. Their main value is visibility and early failure isolation for grid bootstrapping rather than behavioral validation.
