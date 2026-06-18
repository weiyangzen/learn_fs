# sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.hh

## Purpose

This header declares the virtual redirector abstraction and singleton registry used to emulate redirector responses from metadata files such as Metalink documents.

## Important APIs, Types, And Functions

`RedirectJob` is a `Job` that runs a message handler on a synthetic redirect message. `VirtualRedirector` declares `HandleRequest`, `Load`, metadata accessors (`GetTargetName`, `GetCheckSum`, `GetSupportedCheckSums`, `GetSize`, `GetReplicas`), and `Count`. `RedirectorRegistry` exposes `Instance`, destructor, `Register`, `RegisterAndWait`, `Get`, and `Release`. Private `RegisterImpl` and `ConvertLocalfile` support implementation details.

## Control Flow

Clients register a metadata URL before use, obtain redirector responses indirectly through `PostMaster::Redirect`, and call `Release` when done. The registry is a non-copyable singleton backed by a map from URL location to redirector pointer and reference count.

## State And Persistence Behavior

The registry stores `RedirectorMap` in memory and protects it with `XrdSysMutex`. Redirectors are owned by the registry. No on-disk state is written by the registry.

## Dependencies And Integration Points

The header depends on XRootD response types, URL, JobManager, XrdSys mutexes, and STL containers. Implementations are expected to include concrete redirectors such as `MetalinkRedirector`.

## Risks And Edge Cases

`Get` returns a raw pointer and does not retain it. The registry API relies on external register/release discipline. `VirtualRedirector::GetReplicas` returns a const reference, so concrete redirector lifetime must outlive readers.

## Test Signals

Interface tests should use a fake `VirtualRedirector` or Metalink fixture to validate ref-counted registration, raw-pointer lookup, release deletion, and metadata accessor behavior.
