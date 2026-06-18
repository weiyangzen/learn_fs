# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.hh

## Purpose

This header declares `XrdFrcReqAgent`, the manager for one FRM operation queue family and its priority request files.

## Important APIs, Types, and Functions

The class exposes `Add`, `Del`, two `List` overloads, `NextLFN`, `Ping`, and `Start`. It stores an array of `XrdFrcReqFile*` indexed by priority, queue persona/name, default ping message, instance name, and queue id. Static `c2sFN` stores the transfer daemon UDP path.

## Control Flow

An agent is constructed for an operation type, started with a queue path/mode, then receives add/delete/list calls from `XrdFrcProxy`.

## State and Persistence Behavior

Priority request files persist queued work. The agent's in-memory state owns pointers to those files for process lifetime.

## Dependencies and Integration Points

The header includes `XrdFrcReqFile.hh` and `XrdFrcRequest.hh`. It is consumed by the proxy and compiled into `XrdServer`.

## Risks and Edge Cases

The destructor does not delete request-file pointers. Copy/move are not disabled, so accidental copies would duplicate raw pointers. Callers must call `Start()` before `Add()` to initialize `rQueue`.

## Test Signals

Tests should validate lifecycle assumptions and null/unstarted behavior through implementation tests.
