# sources/distributed-fs/xrootd/python/src/Utils.cc

## Purpose
This source implements shared PyXRootD utility functions for callback validation, type initialization, and checked integer conversion from Python objects to unsigned C/C++ numeric types.

## Important APIs, Types, and Functions
`IsCallable` checks `PyCallable_Check`, sets `TypeError` on failure, and increfs valid callbacks. `InitTypes` prepares `URLType`. Numeric helpers are `PyIntToUlong`, `PyObjToUlong`, `PyObjToUint`, `PyObjToUshrt`, and `PyObjToUllong`.

## Control Flow
Integer helpers validate type/range, translate Python conversion errors into more specific messages, reject negative values, and write through output pointers. `PyObjToUint` and `PyObjToUshrt` layer range narrowing on top of unsigned long conversion. `PyObjToUllong` currently routes `PyLong_Check` inputs through unsigned-long conversion first.

## State and Persistence
No persistent state. `IsCallable` mutates callback reference counts. `InitTypes` mutates Python type initialization state.

## Dependencies and Integration Points
Depends on `Utils.hh` and `PyXRootDURL.hh`. Used by async handlers, file methods, chunk iterator, and other argument-parsing paths.

## Risks and Test Signals
Some branches are unreachable because Python 3 integers are always `PyLong_Check`; `PyObjToUllong` may unintentionally limit to unsigned long rather than full unsigned long long on platforms where sizes differ. Callback incref must be paired by async final-response decref. Tests should cover negative, non-integer, overflow boundary values for each helper and callback reference counting.
