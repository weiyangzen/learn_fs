# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.hh

## Purpose

This header declares `XrdXrootdTransit`, a concrete `XrdXrootd::Bridge` implemented by subclassing `XrdXrootdProtocol`. It allows in-process protocol bridging while reusing xroot request handlers.

## Important APIs, types, and functions

Public methods include `Alloc()`, static `Init()`, `ReqTable()`, `Run()`, `Process()`, `Recycle()`, `Disc()`, `Proceed()`, `Redrive()`, `Attn()`, `Send()` overloads, `setSF()`, and `SetWait()`. Private helpers include `Fail()`, `Fatal()`, `ReqWrite()`, `RunCopy()`, `Wait()`, and `WaitResp()`. Nested `SchedReq` adapts member callbacks to `XrdJob`.

## Control flow

The bridge is allocated from `TranStack`, initialized with a link and result callback, substitutes itself as the link protocol, and accepts one active injected request at a time. Scheduled jobs resume after waits or after deferred processing.

## State and persistence behavior

Private state tracks the original protocol, result object, copied args, run status, wait totals/max, reinvocation flags, write buffers, protocol name, creation time, and wait condition variables. All state is per-live bridge object and in-memory.

## Dependencies and integration points

The header depends on atomics, XRootD object pools, bridge interfaces, scheduler jobs, and `XrdXrootdProtocol`. It integrates with `XrdXrootdTransPend`, `XrdXrootdTransSend`, and response async routing.

## Risks and edge cases

Subclassing the full protocol object gives reuse but also inherits a large amount of mutable session state. Only one active bridged request is allowed; callers must handle `Run()` failure on re-entry. Wait scheduling and condition-variable state must be cleaned during recycle.

## Test signals

Tests should validate object-pool reuse, one-request-at-a-time enforcement, wait settings, callback scheduling, and cleanup of pending wait state.
