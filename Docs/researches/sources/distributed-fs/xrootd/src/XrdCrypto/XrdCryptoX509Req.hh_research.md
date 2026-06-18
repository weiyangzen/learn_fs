# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoX509Req.hh

## Purpose

`XrdCryptoX509Req.hh` declares the abstract interface for certificate-signing requests used mainly by proxy certificate workflows.

## Important APIs and Types

`XrdCryptoX509Reqdata` is an opaque backend pointer. The class exposes validity, opaque access, request public key access, bucket export, dump, subject and subject hash, extension lookup, signature verification, and a simple integer version field.

## Control Flow

Consumers obtain request objects through factory hooks, inspect/export them, and pass them into proxy-signing functions.

## State and Persistence Behavior

The base stores only `version`, initialized by the constructor and managed by `Version()`/`SetVersion()`. Concrete implementations manage backend request data.

## Dependencies and Integration Points

It depends on `XrdSutBucket` and `XrdCryptoRSA`. Factory proxy hooks use this type for create/sign request operations.

## Risks and Edge Cases

The interface exposes borrowed string pointers and opaque backend data. Implementations must keep these valid for the request lifetime.

## Test Signals

Tests should verify version metadata, request export, extension access, and interoperability with proxy signing hooks.
