# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpListdir.cc

## Purpose
`XrdClHttpOpListdir.cc` implements `CurlListdirOp`, a WebDAV `PROPFIND Depth: 1` directory listing operation that converts XML multistatus responses into XrdCl `DirectoryList` entries.

## Important APIs and Functions
`Setup` sets the write callback, request data pointer, `CUSTOMREQUEST` to `PROPFIND`, and `Depth: 1`. `WriteCallback` accumulates the XML response with a 10 MB cap. `ParseProp` extracts resource type, content length, last modified time, href, and executable bit. `ParseResponse` extracts a single DAV response entry. `Success` parses the XML, skips the first entry representing the directory itself, and fills a `DirectoryList` or `DirectoryListResponse`.

## Control Flow
After curl success, the operation parses XML with TinyXML. It requires root `D:multistatus`, iterates `D:response` elements, rejects malformed entries, and converts each child entry into a `ListEntry` with host address, name, and `StatInfo` flags.

## State and Persistence
The operation does not mutate remote state. It stores response-info preference, host address, and the accumulated response body.

## Dependencies and Integration Points
It depends on TinyXML, XrdCl directory/stat response types, HTTP response-info wrappers, and `Filesystem::DirList`. Namespaces are handled by string comparisons against `D:` and `lp1:` prefixes.

## Risks and Test Signals
XML parsing is prefix-specific and assumes a depth-one response where the first entry is the directory itself. The `href` parsing is marked not robust. Tests should cover namespace variants, missing fields, invalid sizes/dates, large response rejection, executable flag, directory size defaulting to zero, and response-info propagation.
