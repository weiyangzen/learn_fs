# sources/test-tools/pynfs/nfs4.1/server41tests/st_debug.py

## Purpose
`st_debug.py` contains ad hoc/debug-oriented server tests for open/delegation behavior, simple read/write, concurrent write/getattr deadlocks, and early layout/device-list checks. It is commented out of `server41tests.__all__`.

## Important APIs, Types, and Functions
- `testSupported2` probes open delegation handling across two clients.
- `testReadWrite` creates a file, writes, reads, and closes.
- `testDeadlock` sends multiple asynchronous write/getattr compounds on separate slots.
- `testLayout` and `testGetDevList` test layout and device-list basics.

## Control Flow
The tests build lower-level open operations directly, use sessions created from raw clients, and issue compounds manually. `testDeadlock` starts four async compounds and then listens for each result.

## State and Persistence Behavior
It exercises open stateids, delegation recall, file contents, asynchronous slot state, and pNFS layout/device state. Debug tests leave more printed output than normal tests.

## Dependencies and Integration Points
The module depends on `st_create_session`, environment helpers, generated NFS types, and `nfs_ops`. Layout tests assume helpers such as `get_blocksize` and `use_obj`, but the imports appear incomplete for those names in this file.

## Risks and Edge Cases
Several visible issues make this file unsuitable for default runs: text strings instead of bytes in some owners/data, undefined variables (`res`, `sess1`) in layout paths, and missing imports for helper names. Its exclusion from `__all__` matches these risks.

## Test Signals
When run manually after fixes, useful signals would be successful open/read/write/close, no deadlock under async write/getattr load, and `GETDEVICELIST` success for block-layout exports.
