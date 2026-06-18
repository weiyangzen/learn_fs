# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.cc

## Purpose

This file implements SSI utility helpers for formatting byte buffers, mapping and returning errors, and asynchronously posting SSI error responses. It is shared support code for SSI request/responder paths such as `XrdSsiTaskReal`.

## Important APIs, types, and functions

`XrdSsiUtils::b2x` converts a byte buffer to a truncated hexadecimal string with an overflow suffix. `Emsg` formats an SFS-style error, logs it through `XrdSsi::Log`, and stores it in an `XrdOucErrInfo`. `GetErr`, `MapErr`, and `SetErr` translate `XrdCl::XRootDStatus` into errno-style values and SSI error text. `RetErr` schedules a `PostError` job that binds a request to a temporary responder and calls `SetErrResponse`.

The local `PostError` class is both an `XrdJob` and an `XrdSsiResponder`. It uses a recursive mutex because setting an error response can synchronously re-enter the responder `Finished` callback.

## Control flow

`RetErr` creates `PostError` with a duplicated error string and schedules it on `XrdSsi::schedP`. `PostError::DoIt` locks, sends the error response if still active, and either deletes itself immediately or lets `Finished` delete it after the responder callback. `Finished` unbinds the request, coordinates with the same mutex, and frees the job when both sides have completed.

## State and persistence behavior

There is no durable persistence. Runtime state is the transient scheduled job, bound request pointer, duplicated error text, error number, and active flag. The utility depends on global `Log` and scheduler pointers declared in namespace `XrdSsi`.

## Dependencies and integration points

The file depends on XRootD protocol error mapping, XrdCl response statuses, SSI request/responder infrastructure, SFS/Ouc error types, `XrdScheduler`, and `XrdSysError`. It is used by SSI task code to convert endpoint errors and by callers needing deferred error delivery to avoid lock clashes.

## Risks and edge cases

`b2x` treats `char` as signed when shifting; masking mitigates output but platform signedness is worth noting. `RetErr` duplicates `eTxt` without a null check before `strdup`. The `PostError` object self-deletes in two different paths and relies on the recursive mutex/`isActive` protocol; changes here can easily create use-after-free or leaks. `Emsg` always returns `SFS_ERROR` and logs the error user from `eDest`, so callers should not expect it to preserve original negative errno sign.

## Test signals

Tests should cover short and truncated `b2x` output, XRootD error-response mapping, internal status mapping when `errNo` is zero, asynchronous `RetErr` delivery with immediate and delayed `Finished`, and error-message/log formatting through `Emsg`.
