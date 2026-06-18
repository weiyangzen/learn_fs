# sources/test-tools/pynfs/nfs4.0/servertests/__init__.py

## Purpose
`servertests/__init__.py` declares the NFSv4 server test modules exported by the package. The `__all__` list is a manifest of test modules that the surrounding pynfs test runner can discover or import, including operation-specific tests, replay/reboot/spoof tests, filesystem-location tests, GSS tests, and delegation tests.

## Important APIs, Types, And Functions
- `__all__` is the only API. It lists module filenames such as `st_access.py`, `st_create.py`, `st_lock.py`, `st_gss.py`, and `st_delegation.py`.
- Inline comments annotate maturity, for example "mostly done", "inprogress", "needs work", or "Not Done at all".

## Control Flow
There is no executable control flow beyond module import. The test framework can use `__all__` to know which modules to enumerate.

## State And Persistence Behavior
No runtime state is stored other than the module-level list. There is no persistence.

## Dependencies And Integration Points
The file is part of the `servertests` package and integrates with Python import semantics and the pynfs test harness. The names align with sibling `st_*.py` modules, including every test file in this work item.

## Risks And Edge Cases
- Entries include `.py` suffixes rather than bare module names, which is a convention the test runner must understand.
- Comments indicate some areas are incomplete; a runner that blindly treats all entries as equally mature may hit known gaps.
- Missing or renamed files would break discovery because this manifest is manually maintained.

## Test Signals
The file has no direct assertions. Its signal is discovery coverage: whether server test modules are visible to the test harness and remain synchronized with the package contents.
