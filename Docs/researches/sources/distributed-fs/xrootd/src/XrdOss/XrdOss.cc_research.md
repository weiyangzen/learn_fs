# sources/distributed-fs/xrootd/src/XrdOss/XrdOss.cc

## Purpose

`XrdOss.cc` provides default base-class behavior for the generic OSS interfaces in `XrdOss.hh`. It supplies no-op or unsupported virtual methods and generic page-read/page-write/vector helpers for storage plugins that do not override them.

## Important APIs, Types, and Functions

Implemented `XrdOss` methods include `Connect`, `Disc`, `EnvInfo`, `Features`, `FSctl`, `Reloc`, `StatFS`, `StatLS`, `StatPF`, `StatVS`, `StatXA`, and `StatXP`. Implemented `XrdOssDF` helpers include `Fctl`, synchronous/asynchronous `pgRead`, synchronous/asynchronous `pgWrite`, range-list preread `Read`, `ReadV`, and `WriteV`.

## Control Flow

Most `XrdOss` methods return `-ENOTSUP` or no-op defaults. `pgRead()` calls the normal byte `Read()` then computes page checksums into `csvec` when supplied. Async `pgRead`/`pgWrite` perform the synchronous operation into `XrdSfsAio::Result` and call completion callbacks. `pgWrite()` optionally verifies supplied checksums before writing. `ReadV` and `WriteV` iterate vector entries, require full transfer for each entry, and return `-ESPIPE` on short I/O.

## State and Persistence Behavior

The base helpers do not own persistent state. They operate on virtual file objects and may update `XrdSfsAio` result fields. `pgwEOF` exists in the base object but is not modified here.

## Dependencies and Integration Points

The file integrates with `XrdOucPgrwUtils` for page checksum calculation/verification and `XrdSfsAio` for async completion. Storage plugins inherit these defaults unless they advertise and implement more capable behavior.

## Risks and Edge Cases

Default async page operations are synchronous completions, so callers must not assume real asynchronous dispatch unless feature flags and overrides say so. Short vector I/O is treated as `-ESPIPE`, which may differ from POSIX callers' expectations. Checksum verification returns `-EDOM`.

## Test Signals

Tests should cover default unsupported methods, page checksum calculation, checksum verification failure, async completion callbacks, vector full-read/write success, and vector short-I/O failure.
