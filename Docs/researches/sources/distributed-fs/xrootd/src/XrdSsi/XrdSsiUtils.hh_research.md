# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.hh

## Purpose

This header declares SSI utility functions used for diagnostics and error translation. It isolates common helper APIs behind a stateless `XrdSsiUtils` class.

## Important APIs, types, and functions

The public static API includes `b2x`, `Emsg`, `GetErr`, `MapErr`, `RetErr`, and `SetErr`. Forward declarations keep the header light for `XrdCl::XRootDStatus`, `XrdOucErrInfo`, `XrdSsiErrInfo`, and `XrdSsiRequest`.

## Control flow

The header has no runtime control flow. It documents call shape: status-to-error helpers fill strings or `XrdSsiErrInfo`, `RetErr` posts an asynchronous request error, and `Emsg` logs plus fills an output error object.

## State and persistence behavior

The class has no member state and no persistence. The default constructor/destructor are empty; all meaningful operations are static.

## Dependencies and integration points

The declarations are used by SSI task/session code and bridge XrdCl, SSI, SFS, and Ouc error systems. The implementation relies on global SSI logging and scheduling.

## Risks and edge cases

Because the helper methods accept raw buffers and references to external error objects, callers must provide correctly sized output buffers and live request/error objects. `RetErr` in particular assumes the request remains valid until the scheduled job binds and responds.

## Test signals

Compilation coverage should include consumers that only need declarations. Behavioral tests belong with the implementation and should validate error mapping and asynchronous error posting.
