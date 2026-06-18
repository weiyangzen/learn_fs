# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsTalk.cc

## Purpose

`XrdCmsTalk.cc` implements low-level CMS request/response framing over `XrdLink`. It serializes `CmsRRHdr` headers, length-prefixed payloads, and CMS response/error records using network byte order and vectored writes.

## Important APIs and Functions

`Attend()` receives a complete header, decodes `Hdr.datalen` with `ntohs`, validates caller buffer capacity, and receives the payload. `Complain()` sends a `kYR_error` response with an integer error code and NUL-terminated message. `Request()` sets `Hdr.datalen` and sends header plus body. `Respond()` sends a `CmsResponse` with response code and a four-byte value overhead followed by optional payload.

## Control Flow

Receive flow is strict: header must arrive fully, length must fit, and payload must arrive fully before success. Send flow uses two-entry `iovec` arrays and treats negative `Send()` return as failure. Error methods return string literals for callers to log or act on.

## State and Persistence Behavior

This file is stateless. It mutates the supplied header's length field and writes protocol messages to the link.

## Dependencies and Integration Points

It depends on `XProtocol/YProtocol.hh` for CMS wire structures and response codes, `XrdLink` for I/O, and C networking byte-order helpers. It is used by CMS protocol participants that need a compact request/response helper independent of the full protocol class.

## Risks and Edge Cases

`Request()` casts payload length to `unsigned short`, so callers must not pass bodies above 65535 bytes. `Respond()` includes a fixed four-byte overhead in `datalen`; mismatches with protocol readers would desynchronize framing. `Attend()` does not validate null buffers for nonzero data and treats partial reads as generic failures without preserving errno.

## Test Signals

Tests should round-trip headers and payloads with boundary lengths, oversized payload rejection, partial read/write simulation, and exact wire layout for `Complain()` and `Respond()`.
