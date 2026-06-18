# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.hh

## Purpose

`XrdCmsTalk.hh` declares a static helper class for CMS link-level message exchange. It centralizes request, response, complaint, and receive operations around `CmsRRHdr`.

## Important APIs and Types

The public methods are `Attend()`, `Complain()`, `Request()`, and `Respond()`. `Attend()` returns a nullable error string and fills response length. `Complain()` returns an integer status after sending an error response. `Request()` and `Respond()` return nullable error strings after link sends.

## Control Flow

The header's API makes callers responsible for allocating payload buffers, selecting timeouts, and interpreting string errors. The default receive timeout is 5000 milliseconds.

## State and Persistence Behavior

The class has no member state. It mutates caller-supplied headers and communicates through an `XrdLink`.

## Dependencies and Integration Points

It includes `XProtocol/YProtocol.hh` for CMS wire types and forward-declares `XrdLink`. It integrates with CMS protocol code that already owns links and buffers.

## Risks and Edge Cases

The static API has no type-level protection for buffer size versus header length and no support for payloads above the 16-bit protocol length. Callers must check returned error strings consistently.

## Test Signals

Mock-link tests can assert timeout forwarding, length encoding, and correct handling of short reads/writes.
