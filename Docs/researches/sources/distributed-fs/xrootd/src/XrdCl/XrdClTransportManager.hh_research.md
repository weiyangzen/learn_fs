# sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.hh

## Purpose

This header declares `TransportManager`, the protocol-to-transport registry used by XrdCl channel creation.

## Important APIs, Types, and Functions

`TransportFactory` is a function pointer returning a `TransportHandler *`. Public methods are constructor, destructor, `RegisterFactory(protocol, factory)`, and `GetHandler(protocol)`. Private maps store cached handlers and registered factories.

## Control Flow

The API supports eager built-in handlers and lazy factory-created handlers. Callers ask for a handler by URL protocol and get either a cached handler, a newly factory-created handler, or null.

## State and Persistence Behavior

The manager owns cached handler pointers for its lifetime. Factories are non-owning function pointers. There is no persistence.

## Dependencies and Integration Points

The header uses C++ maps/strings and forward-declares `TransportHandler`. It is consumed by postmaster/channel initialization code.

## Risks and Edge Cases

Raw handler pointers require clear ownership. The class does not declare copy prevention; accidental copying would duplicate owning pointers. No thread-safety guarantees are declared.

## Test Signals

Compile/link tests, registry behavior tests, and copy-prevention/leak checks are the relevant signals.
