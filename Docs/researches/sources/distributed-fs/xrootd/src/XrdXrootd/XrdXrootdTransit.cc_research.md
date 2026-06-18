# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.cc

## Purpose

This file implements `XrdXrootdTransit`, the bridge that lets another protocol inject xroot requests into the xroot protocol stack and receive results through a `Bridge::Result` callback instead of raw socket responses.

## Important APIs, types, and functions

`Alloc()` obtains and initializes a transit object. `Init()` has static and per-instance forms. `Run()` accepts an xroot request header and optional data. `Process()` interleaves the real protocol and injected xroot request. `Send()` overloads translate xroot responses into bridge callbacks. `Wait()`, `WaitResp()`, `Redrive()`, `Proceed()`, `Attn()`, and `AttnCont()` handle wait and async response flows. `Disc()` and `Recycle()` dismantle the bridge.

## Control flow

Initialization binds the transit protocol to the link, arms bridge mode, sets security/entity fields, registers monitoring, and marks the session logged in. `Run()` validates the request against `ReqTable()`, unmarshals lengths, copies arguments into `argp`, handles partial write data specially, and marks the bridge active. `Process()` lets the original protocol run, then dispatches the injected request through `XrdXrootdProtocol::Process()` or `Process2()`. Normal responses call `Bridge::Result` methods for data, done, errors, redirects, waits, or files.

## State and persistence behavior

Transit stores borrowed real protocol/result/link/security pointers, copied request arguments for redrive, wait counters, wait condition state, run status atomics, and monitor/client identity inherited from `XrdXrootdProtocol`. It has no durable persistence; it only mediates live requests. Pending `waitresp` state is stored in `XrdXrootdTransPend`.

## Dependencies and integration points

It depends on security entities, links, buffers, SFS, scheduler, stats, tracing, pending queue, sendfile adapter, and the base protocol class. It is used by protocol bridge APIs and by static response attention routing.

## Risks and edge cases

Concurrency is delicate: `runStatus`, `runWait`, `waitPend`, scheduled jobs, and recycle/disconnect must agree to prevent re-entry or use-after-free. `Run()` returns `true` even after some validation failures by storing `runError`, so callers must drive processing to receive the error callback. Wait-time accounting can cancel long waits with `kXR_Cancelled`. Partial write bridging depends on `do_WriteSpan` and buffer lifetime callbacks.

## Test signals

Tests should cover supported/unsupported request table entries, argument copy and redrive after wait, wait notification and timeout behavior, waitresp attention completion, recycle while waiting, bridge error/data/done/redir/file callbacks, re-entry rejection, and disconnect restoration of the original protocol.
