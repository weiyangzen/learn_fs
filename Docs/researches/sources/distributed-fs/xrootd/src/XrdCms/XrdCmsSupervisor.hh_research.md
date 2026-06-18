# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.hh

## Purpose

`XrdCmsSupervisor.hh` declares the static supervisor facade used to initialize and run a supervisor-side CMS listener for redirector communication. It exposes no per-instance behavior; all meaningful state is static.

## Important APIs and Types

`superOK` is a public readiness flag. `Init()` creates and binds the supervisor socket. `Start()` enters the accept/process loop. `NetTCPr` is a private static `XrdInet *` listener shared by those methods.

## Control Flow

Callers are expected to call `Init()` once and then `Start()` if initialization succeeded. Constructor/destructor are trivial and unused for lifecycle management.

## State and Persistence Behavior

The class persists process state in static members only. Socket persistence and configuration changes are handled by the implementation file.

## Dependencies and Integration Points

The only declaration dependency is the forward declaration of `XrdInet`, but implementation links it to Xrd network and CMS protocol subsystems.

## Risks and Edge Cases

The header advertises public static mutable state with no synchronization. Multiple `Init()` calls could leak or overwrite listener state unless external startup code prevents reinitialization.

## Test Signals

Tests should assert that `superOK` changes only after successful initialization and that `Start()` is not called before `NetTCPr` is created.
