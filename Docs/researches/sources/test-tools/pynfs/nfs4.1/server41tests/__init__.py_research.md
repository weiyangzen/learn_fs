# sources/test-tools/pynfs/nfs4.1/server41tests/__init__.py

## Purpose
`server41tests/__init__.py` declares the server-side NFSv4.1 test modules exported by the package. The test runner uses `__all__` as a module inventory.

## Important APIs, Types, and Functions
- `__all__` is a list of test module filenames, including exchange/session lifecycle tests, security-info tests, sequence/trunking/open/delegation tests, pNFS tests, sparse/flex/xattr tests, courtesy tests, and callback tests.

## Control Flow
Importing the package exposes only the modules listed in `__all__` to `from server41tests import *` style discovery. Some modules are commented out, including `st_lookup.py`, `st_debug.py`, and `st_loop`.

## State and Persistence Behavior
There is no runtime state beyond the static module list.

## Dependencies and Integration Points
The file integrates with the pynfs `testmod` discovery layer and the server test runner. The presence of filenames rather than module objects suggests the runner may treat entries as loadable script names.

## Risks and Edge Cases
Commented-out modules may contain useful tests but are intentionally excluded. Duplicate or missing filenames here directly affect coverage. The list mixes active protocol areas and feature-gated tests, so runners must still honor each test's `FLAGS`.

## Test Signals
Discovery should include the requested active modules such as `st_exchange_id.py`, `st_compound.py`, `st_create_session.py`, `st_destroy_session.py`, `st_destroy_clientid.py`, `st_delegation.py`, `st_block.py`, `st_current_stateid.py`, `st_courtesy.py`, and `st_callback.py`.
