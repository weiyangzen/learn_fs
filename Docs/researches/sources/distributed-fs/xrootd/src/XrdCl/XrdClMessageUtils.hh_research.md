# sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.hh

## Purpose

This header declares message send parameters, synchronous/null response helpers, request construction helpers, and utility functions for sending, redirecting, rewriting, and xattr body construction.

## Important APIs, Types, And Functions

`SyncResponseHandler` blocks callers until `HandleResponse` stores a status and response. `NullResponseHandler` deletes itself when a response arrives and ignores the payload. `MessageSendParams` carries timeout, expiry, load balancer, redirect/chunk/stateful flags, host list, chunk list, redirect limit, kernel buffer, and CRC32C digests.

`MessageUtils` declares `WaitForStatus`, templated `WaitForResponse`, templated `CreateRequest`, `SendMessage`, `RedirectMessage`, `ProcessSendParams`, `RewriteCGIAndPath`, `MergeCGI`, `CreateXAttrVec`, and templated `CreateXAttrBody`.

## Control Flow

Synchronous callers create a `SyncResponseHandler`, submit an operation, wait on its condition variable, then extract and delete the status through `WaitForStatus` or extract a typed response through `WaitForResponse`. Request creation allocates a zeroed `Message` sized for a request struct plus payload. `CreateXAttrBody` builds the fattr body after the header and updates `dlen`.

## State And Persistence

`SyncResponseHandler` holds status/response pointers and a condition variable until consumed. `MessageSendParams` owns no memory by default but may transfer pointers to handlers during send. All state is transient.

## Dependencies And Integration Points

It includes response types, `URL`, `Message`, `XrdSysKernelBuffer`, and `XrdSysPthread`. It forward-declares `LocalFileHandler` and integrates with file/filesystem APIs, local redirects, transports, and xattr operations.

## Risks

`SyncResponseHandler::WaitForResponse` waits indefinitely if a response is never delivered. `NullResponseHandler` does not delete status/response/host payloads, relying on upstream behavior or intentionally leaking ignored responses. `WaitForResponse` sets the `AnyObject` to an `int*` null to detach the typed response; this depends on `AnyObject` semantics. `MessageSendParams` exposes raw pointers with unclear ownership until send-time conventions are followed.

## Test Signals

Useful tests include synchronous success/error waits, typed response extraction and ownership, request buffer sizing/zeroing, xattr body layout with path prefix, send parameter defaults, and static analysis of raw pointer ownership in `hostList`, `chunkList`, and kernel buffer fields.
