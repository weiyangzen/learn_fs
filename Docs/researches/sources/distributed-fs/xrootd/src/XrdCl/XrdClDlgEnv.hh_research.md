# sources/distributed-fs/xrootd/src/XrdCl/XrdClDlgEnv.hh

## Purpose
Provides a tiny singleton helper for controlling the `XrdSecGSIDELEGPROXY` process environment variable used by GSI credential delegation.

## Important APIs, Types, And Functions
`DlgEnv::Instance()` returns a function-local static singleton. `Enable()` sets `XrdSecGSIDELEGPROXY=1`, `Disable()` sets it to `0`, and the destructor unsets it. Copy construction and assignment are declared private and undefined to prevent copying.

## Control Flow
Callers, notably copy/TPC code paths, obtain `DlgEnv::Instance()` and call `Enable` or `Disable` before operations needing delegation behavior. At process shutdown the singleton destructor clears the environment variable.

## State And Persistence
No C++ member state is stored. The persistent side effect is process-wide environment state via `setenv` and `unsetenv`. This affects all threads and subsequent security plugin calls in the same process.

## Dependencies And Integration Points
Depends only on `<cstdlib>`. It integrates with `XrdSecgsi` behavior, where `XrdSecGSIDELEGPROXY` is read by the GSI security protocol. `XrdClThirdPartyCopyJob` and `XrdClCopy` include this helper.

## Risks
Environment mutation is global and not synchronized here. Concurrent operations needing different delegation settings can interfere. Destructor unconditionally unsets the variable, so embedding applications that set it independently may lose their value at shutdown. `setenv` failure is ignored.

## Test Signals
Tests should verify enable/disable values, destructor cleanup in a controlled process, and copy/TPC flows that require delegated and non-delegated GSI behavior. Threaded tests should avoid assuming isolation unless higher-level code serializes access.
