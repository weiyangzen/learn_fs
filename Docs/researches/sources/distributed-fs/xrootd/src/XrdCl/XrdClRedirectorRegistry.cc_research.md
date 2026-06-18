# sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.cc

## Purpose

This file implements a singleton registry for virtual metadata redirectors, currently Metalink redirectors. It lets the client register a metadata URL, later route requests through a local virtual redirector, and release redirectors when users are done.

## Important APIs, Types, And Functions

`RedirectJob::Run` delivers a synthetic message to a `MsgHandler` via `Examine` and `Process`. `RedirectorRegistry::Instance` returns the singleton. `RegisterImpl` normalizes localfile URLs, validates supported protocols/formats, ref-counts existing redirectors, creates `MetalinkRedirector` for Metalink URLs, loads it, and stores it. `Register`, `RegisterAndWait`, `Get`, and `Release` wrap registry operations. `ConvertLocalfile` maps deprecated `root://localfile//...` URLs to `file://localhost/...` when enabled.

## Control Flow

Registration first converts deprecated localfile syntax, rejects URLs without paths and non-local `file://` URLs, then locks the registry. Existing entries increment their user counter and optionally notify a handler with success. New Metalink entries allocate and load a redirector; successful loads are stored with count one. `RegisterAndWait` uses `SyncResponseHandler` plus `MessageUtils::WaitForStatus`. `Release` decrements the count and deletes/erases at zero.

## State And Persistence Behavior

`pRegistry` maps `URL::GetLocation()` to `(VirtualRedirector*, useCount)`. It is protected by `pMutex`. The registry owns redirectors and deletes them in `Release` or destructor. Metalink content is loaded by redirector implementation; this file only stores the object.

## Dependencies And Integration Points

The file depends on `MetalinkRedirector`, `PostMasterInterfaces`, `DefaultEnv`, constants, logging, and response utilities. `PostMaster::Redirect` calls `RedirectorRegistry::Get(url)` and delegates to `VirtualRedirector::HandleRequest`.

## Risks And Edge Cases

`RegisterImpl` holds the mutex while constructing/loading a new `MetalinkRedirector`; if loading invokes callbacks that reenter the registry, that could be risky. `Get` returns a raw pointer without incrementing the use count, so callers must coordinate lifetime with prior `Register`. Deprecated URL conversion depends on `LocalMetalinkFile`. Only Metalink is supported; other metadata formats return `errNotSupported`.

## Test Signals

Tests should register Metalink URLs asynchronously and synchronously, ref-count duplicate registration/release, verify deprecated localfile conversion and warning path, reject non-local file URLs and URLs without paths, and route a message through `PostMaster::Redirect` to a fake handler.
