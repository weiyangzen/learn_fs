# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3File.hh

## Purpose
Declares the `XrdClS3::File` final `XrdCl::FilePlugIn` implementation used for S3 object I/O through XRootD's HTTP client.

## Important APIs, Types, and Functions
The class overrides the file plugin surface: `Open`, `Close`, `IsOpen`, `Read`, `PgRead`, `VectorRead`, `Write`, `Stat`, `GetProperty`, and `SetProperty`. Private `GetFileHandle()` lazily constructs the HTTPS handle. Nested `S3HeaderCallout` implements `XrdClHttp::HeaderCallout::GetHeaders()`.

## Control Flow
Callers interact through the standard XrdCl file API. The first open resolves the S3 URL and configures a wrapped HTTP file; subsequent file operations are forwarded to that handle. The nested header callout is invoked by the HTTP layer for each request and calls the factory signing function.

## State and Persistence Behavior
The object stores open status, original/open URL data, a logger pointer, an in-memory property map, a wrapped `XrdCl::File`, and an embedded header callout. No persistent filesystem state is owned by the wrapper.

## Dependencies and Integration Points
Includes `XrdClHttpHeaderCallout.hh` and `XrdClFile.hh`. Integrates with `XrdClS3Factory` at implementation time and with the HTTP plugin through a property that points at `m_header_callout`.

## Risks and Edge Cases
The declared `m_open_flags` is present but not used by the implementation read. Thread-safety covers property access but not all file lifecycle state. Header callout pointer wiring requires object lifetime discipline.

## Test Signals
Compile/API tests should ensure all `XrdCl::FilePlugIn` overrides match the current XrdCl ABI. Behavior tests should cover property get/set, open lifecycle, and header callout invocation.
