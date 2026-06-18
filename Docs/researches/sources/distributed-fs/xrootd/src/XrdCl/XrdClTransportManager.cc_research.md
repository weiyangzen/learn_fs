# sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.cc

## Purpose

This file implements a registry/cache for protocol-specific `TransportHandler` objects. It ships with built-in XRootD transports for root/xroot and secure roots/xroots protocols.

## Important APIs, Types, and Functions

The constructor populates `pHandlers` with new `XRootDTransport` instances for `"root"`, `"xroot"`, `"roots"`, and `"xroots"`. The destructor deletes cached handlers. `RegisterFactory` is intended to register protocol factories. `GetHandler` returns an existing handler or creates one from a registered factory.

## Control Flow

Lookup first checks the handler cache. If no handler exists, `GetHandler` checks `pFactories`; missing factory returns null. If a factory exists, it is called once and the produced handler is cached for later calls.

## State and Persistence Behavior

State is in-memory maps of protocol to handler and protocol to factory. The manager owns all cached handlers and deletes them on destruction. No persistent registry exists.

## Dependencies and Integration Points

It depends on `XrdClTransportManager.hh` and `XrdClXRootDTransport.hh`. Channel/postmaster setup uses this manager to obtain the transport implementation for a URL protocol.

## Risks and Edge Cases

`RegisterFactory` currently returns false when the protocol is absent from `pFactories`, then assigns only when it already exists. Because the map starts empty, this appears to prevent registration of new external factories. There is no duplicate handler cleanup if a factory registration changes after a handler is already cached. The manager is not internally synchronized.

## Test Signals

Tests should assert built-in protocol lookup, unknown protocol null lookup, external factory registration behavior, handler caching, and destructor cleanup under leak checking.
