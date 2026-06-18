## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.cc

Purpose: implements a small value object describing one checksum algorithm mapping between XRootD configuration naming and HTTP digest naming.

Important APIs and control flow: the constructor stores the XRootD config digest name, the HTTP name, a base64-padding flag, and precomputes a lowercase HTTP name using `std::transform(::tolower)`. Getters return copies of the three strings and the padding flag.

State and persistence: all state is immutable after construction by convention, stored in private string/bool members. There is no persistence or external side effect.

Dependencies and integration: used by `XrdHttpChecksumHandlerImpl` to build supported checksum maps and configured checksum vectors.

Risks and test signals: `::tolower` on plain `char` can be undefined for negative signed-char values, though algorithm names are ASCII. Tests should validate lowercase conversion, HTTP/config aliases, and padding flags for supported checksums.
