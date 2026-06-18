# sources/distributed-fs/xrootd/src/XrdCl/XrdClMonitor.hh

## Purpose

This header defines the plugin interface for client-side monitoring. A shared library named by `XRD_CLIENTMONITOR` can provide `XrdClGetMonitor` and receive structured connection, file, copy, checksum, and error events.

## Important APIs, Types, And Functions

`Monitor` is an abstract base class with pure virtual `Event(EventCode, void*)`. Event payload structs are `ConnectInfo`, `DisconnectInfo`, `OpenInfo`, `CloseInfo`, `ErrorInfo`, `TransferInfo`, `CopyBInfo`, `CopyEInfo`, and `CheckSumInfo`. `EventCode` includes `EvCopyBeg`, `EvCopyEnd`, `EvCheckSum`, `EvOpen`, `EvClose`, `EvErrIO`, `EvConnect`, and `EvDisconnect`.

## Control Flow

The client runtime loads the monitor plugin externally and calls `Event` with an event code plus a pointer to the corresponding struct. The plugin casts based on the event code. Constructors initialize numeric counters, pointers, statuses, and timeval fields to safe defaults.

## State And Persistence

The header itself stores no runtime state. Each event struct is transient. Monitoring persistence depends entirely on the plugin implementation; this interface only defines data passed to it.

## Dependencies And Integration Points

It depends on `XrdClFileSystem.hh`, `URL`, `XRootDStatus`, `Status`, and `sys/time.h`. It integrates with connection management, file open/close accounting, copy jobs, checksum validation, and error reporting.

## Risks

The `void*` event payload API is ABI-sensitive and type-unsafe. Plugins must ignore unknown future event codes and must not retain pointers past their validity unless they copy data. Several struct fields are raw pointers to URL/status objects owned elsewhere. Typo-level interface stability matters because external shared libraries compile against this header.

## Test Signals

Signals include loading a test monitor through `XRD_CLIENTMONITOR`, verifying every event code receives the expected struct shape, connection byte/time accounting, file read/write counters, copy begin/end ordering, checksum timing/status reporting, error op-code classification, and ABI compatibility across builds.
