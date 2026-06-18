# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.hh

## Purpose

This header declares `XrdFrcReqFile`, the fixed-record persistent queue file abstraction used by FRM request agents and workers.

## Important APIs, Types, and Functions

Public operations add, cancel, delete/free, get/pop, initialize, list, and format request records. Private state includes lock and request filenames/descriptors, header data, agent-mode flag, file mutex, lock type enum, and recovery list node type.

`FileHdr` records first, last, and free-chain offsets. `rqMonitor` wraps a static mutex used when the object is in agent mode.

## Control Flow

Agents create one request file per operation priority, call `Init()`, then `Add()`/`Can()`/`List()`. Consumers can call `Get()` and `Del()` to pop and free records.

## State and Persistence Behavior

Persistent state lives in the request file and companion lock file. In-memory state caches header fields and descriptor/fname ownership.

## Dependencies and Integration Points

It includes `XrdFrcRequest.hh` and XrdSys mutex wrappers. It integrates with `XrdFrcReqAgent` and `XrdFrcCID` recovery logic.

## Risks and Edge Cases

The destructor does not close file descriptors or free filename strings, so objects are expected to live for process duration. The binary record format is tied to `sizeof(XrdFrcRequest)`. Copy/move operations are not disabled despite raw ownership.

## Test Signals

Tests should exercise lifecycle through the implementation, with special focus on persistent format compatibility and lock-file behavior.
