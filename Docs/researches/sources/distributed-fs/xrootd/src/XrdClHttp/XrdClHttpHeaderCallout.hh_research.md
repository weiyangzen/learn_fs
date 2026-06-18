# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpHeaderCallout.hh

## Purpose
`XrdClHttpHeaderCallout.hh` declares the public extension interface for request header customization in the HTTP plugin.

## Important APIs and Types
`HeaderCallout` defines `HeaderList` as `std::vector<std::pair<std::string, std::string>>` and one pure virtual method, `GetHeaders(verb, url, headers)`, returning a shared pointer to a replacement or augmented header list.

## Control Flow
`File` and `Filesystem` accept a serialized pointer property named `XrdClHttpHeaderCallout`. Operations pass their current verb, URL, and headers through the callout before libcurl setup. The file-specific default callout wraps an optional user callout and may inject PUT `Content-Length`.

## State and Persistence
The interface owns no state. Implementations may be shared externally; the plugin stores raw pointers atomically and does not own them.

## Dependencies and Integration Points
The header depends only on memory, string, utility, and vector. It is installed as a public plugin header and used by `CurlOperation` setup.

## Risks and Test Signals
Because the plugin stores non-owning raw pointers, implementation lifetime must exceed active requests. Tests should cover null return handling, empty header lists, duplicate header behavior, and interaction with file-level Content-Length injection.
