# sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.hh

## Purpose

This header declares `XrdCl::MetalinkRedirector`, a `VirtualRedirector` implementation that serves redirects from replicas listed in a metalink file.

## Important APIs, Types, And Functions

Public methods are `MetalinkRedirector(const std::string&)`, `~MetalinkRedirector`, `Load`, `HandleRequest`, `GetTargetName`, `GetCheckSum`, `GetSupportedCheckSums`, `GetSize`, `GetReplicas`, and `Count`. Private methods include request handling, parsing, initialization finalization, response/error generation, checksum and replica initialization, replica selection, and CGI extraction.

State types include `RedirectList`, `CksumMap`, and `ReplicaList`. Friends `MetalinkOpenHandler` and `MetalinkReadHandler` access private members during asynchronous loading.

## Control Flow

Users construct with the metalink URL and call `Load`. Until loading completes, `HandleRequest` queues `(Message*, MsgHandler*)` pairs. After completion, requests are converted immediately into virtual redirect/error responses.

## State And Persistence

The object stores the metalink URL, a temporary `File`, parsed checksums and replicas, readiness status, target name, file size, pending redirects, and mutex. All persistence is in memory for the lifetime of the redirector.

## Dependencies And Integration Points

It includes `XrdClMessageUtils.hh` and `XrdClRedirectorRegistry.hh`, forward-declares `File`, `Message`, and `XrdOucFileInfo`, and derives from `VirtualRedirector`. It is used by the redirector registry and message handlers when following metalink redirects.

## Risks

The header exposes `GetReplicas` as a non-const reference to internal vector state, so callers can mutate replica order/content. Pending redirects store raw pointers to messages and handlers; they must remain valid until initialization. The checksum type mapping special-cases adler32/a32, so unknown aliases are not normalized.

## Test Signals

Header/API tests should verify virtual redirector polymorphism, loading lifecycle, checksum lookup behavior, supported checksum ordering, replica vector access, pending request behavior, and `Count` semantics for messages with and without `tried` CGI.
