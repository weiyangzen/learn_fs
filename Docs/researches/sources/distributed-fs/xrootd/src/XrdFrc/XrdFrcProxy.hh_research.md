# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.hh

## Purpose

This header declares the FRM request proxy class. It exposes a compact API for adding, deleting, listing, and initializing file-residency queues without exposing request-file implementation details.

## Important APIs, Types, and Functions

`XrdFrcProxy::Add()` creates a request; `Del()` cancels by request id; the two `List()` overloads stream pending LFNs or structured item fields; `Init()` creates queue agents. Operation masks `opGet`, `opPut`, `opMig`, `opStg`, and `opAll` select supported queues.

Nested `Queues` holds incremental list state: offset, priority, queue list mask, current queue, and active flag.

## Control Flow

Users construct a proxy with logger, instance name, and optional debug flag, initialize it for desired operation masks, then call add/delete/list. Listing with `Queues` can resume across calls.

## State and Persistence Behavior

The class stores pointers to `XrdFrcReqAgent` instances and queue path/instance strings. Persistent state is delegated to request agents/files.

## Dependencies and Integration Points

The header includes `XrdFrcRequest.hh` and forward-declares agents, streams, and loggers. It is part of the XrdServer private source set.

## Risks and Edge Cases

The destructor does not delete allocated agents or strings, implying process-lifetime ownership. `Queues` internals are friend-accessed by the proxy and initialized only through its constructor.

## Test Signals

Tests should compile users of the public API and exercise lifecycle through the source implementation.
