# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpQuery.cc

## Purpose
`XrdClHttpOpQuery.cc` implements the success path for `CurlQueryOp`, currently supporting XAttr-style metadata queries.

## Important APIs and Functions
`CurlQueryOp::Success` checks `m_queryCode`. For `XrdCl::QueryCode::XAttr`, it creates an `XrdCl::Buffer` containing the parsed ETag header, packages it into an `AnyObject`, and calls the handler with success. Unsupported query codes log an error and call `Fail`.

## Control Flow
`Filesystem::Query(XAttr)` constructs a `CurlQueryOp`, which inherits stat/header-fetch behavior from `CurlStatOp`. After headers are available, this file converts header state into the XrdCl query response.

## State and Persistence
The operation does not modify remote state. It reads response headers into inherited state and emits a buffer.

## Dependencies and Integration Points
It depends on XrdCl filesystem query codes, buffers, logging, and the inherited `CurlStatOp` setup. File-level `Fcntl` has a separate XAttr JSON path.

## Risks and Test Signals
Only ETag is returned for XAttr here, while `File::Fcntl` returns richer JSON; consumers may see inconsistent metadata shapes. Tests should cover missing ETag, unsupported query code failure, handler ownership, and response status mapping from the inherited stat operation.
