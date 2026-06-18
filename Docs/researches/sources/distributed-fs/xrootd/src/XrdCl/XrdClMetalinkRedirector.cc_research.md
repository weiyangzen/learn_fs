# sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.cc

## Purpose

This file implements a virtual redirector backed by a metalink file. It downloads and parses the metalink, records target/checksum/replica metadata, and answers virtual redirect requests with the next untried replica or a protocol error.

## Important APIs, Types, And Functions

`MetalinkOpenHandler` opens the metalink and starts reading. `MetalinkReadHandler` reads chunks until EOF, accumulates content, parses it, finalizes initialization, and notifies the user. `MetalinkRedirector::Load`, `Parse`, `FinalizeInitialization`, `GetResponse`, `GetErrorMsg`, `HandleRequestImpl`, `HandleRequest`, `Count`, `InitCksum`, `InitReplicas`, `GetReplica`, and `GetCgiInfo` implement the redirector behavior. `DeallocArgs` is a helper for discarded callback payloads.

## Control Flow

`Load` opens the metalink URL with a `File` object created with `DisableVirtRedirect`. On open success, `MetalinkOpenHandler` schedules the first read. `MetalinkReadHandler` appends each `ChunkInfo` into `pContent` and schedules another read while bytes are returned. A zero-byte read closes the file object, parses the metalink using `XrdXmlMetaLink`, finalizes the redirector, handles pending redirect requests, and responds to the user handler.

Requests that arrive before parsing completes are queued in `pPendingRedirects` under `pMutex`. After readiness, `HandleRequestImpl` creates a synthetic `ServerResponse` with `kXR_redirect` and port `-1` for full-URL redirects, or a `kXR_error` message when loading failed or replicas are exhausted.

## State And Persistence

Persistent in-memory redirector state includes `pUrl`, `pFile`, checksum map, replica vector, readiness flag, initialization status, target name, file size, pending redirect list, and mutex. It does not persist to disk. Replica selection is stateless except for reading the request CGI `tried` list.

## Dependencies And Integration Points

It integrates with `File`, response handlers, `DefaultEnv`, `Log`, `JobManager`, `PostMaster`, `RedirectJob`, `VirtualRedirector`, `RedirectorRegistry`, `XrdXmlMetaLink`, `XrdOucFileInfo`, `URL`, `Utils::splitString`, and XRootD protocol response structs. The environment keys `GlfnRedirector` and `TlsMetalink` alter parsing and replica protocol rewriting.

## Risks

The read handler accumulates the whole metalink in memory without an explicit size cap. `FinalizeInitialization` calls `HandleRequestImpl` while holding `pMutex`, which can be risky if future redirect handling re-enters the redirector. `GetCgiInfo` searches for the key substring after `?` rather than parsing parameters exactly, so keys embedded in other names could match. `Count` subtracts vector iterators and returns `int`, which assumes vector size fits. Invalid or oversized replica URLs are silently skipped; an empty replica list becomes a runtime no-replicas error.

## Test Signals

Tests should cover successful metalink load, malformed XML, metalink with multiple files, empty replica list, checksum extraction including adler32/a32 mapping, target and size extraction, pending request replay, `tried` CGI filtering, `TlsMetalink` root-to-roots rewriting, synthetic redirect response wire layout, and callback cleanup on open/read failures.
