# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.hh

## Purpose

This header declares the S3 full-download helper used by the S3 filesystem layer.

## Important APIs, types, and functions

`XrdClS3::DownloadUrl(const std::string &url, XrdClHttp::HeaderCallout *header_callout, XrdCl::ResponseHandler *handler, time_t timeout)` starts an asynchronous full-object download and returns the immediate XRootD status from initiating the open/read chain.

## Control flow

Callers pass an already generated HTTPS URL and optional S3 signing header callout. The implementation opens the URL through the HTTP plugin and eventually calls the supplied response handler with either an error status or an owned `XrdCl::Buffer`.

## State and persistence behavior

The header owns no state. Runtime state is in the implementation's response handlers.

## Dependencies and integration points

It includes `XrdClS3Filesystem.hh` for `XrdClHttp::HeaderCallout` visibility and XRootD response headers. It is used by S3 filesystem stat/listing helpers.

## Risks and edge cases

The declaration exposes a raw `HeaderCallout *`; lifetime is the caller's responsibility. The API returns only initiation status, while final success/failure is asynchronous through `handler`.

## Test signals

Compile coverage verifies the S3 filesystem integration. Behavioral tests should target the `.cc` implementation.
