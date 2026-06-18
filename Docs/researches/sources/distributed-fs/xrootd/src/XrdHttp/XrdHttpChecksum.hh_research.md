## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.hh

Purpose: declares `XrdHttpChecksum`, a simple checksum metadata holder for the HTTP checksum negotiation layer.

Important APIs/types: constructor accepts XRootD config digest name, HTTP RFC-style name, and whether the checksum value needs base64 padding. Getters expose XRootD config name, HTTP name, lowercase HTTP name, and padding requirement.

State and persistence: private members store the names and flag. The object is used as static/shared metadata by checksum handler maps.

Dependencies and integration: depends only on `<string>`, making it lightweight and reusable in unit tests. It is included by checksum handler headers.

Risks and test signals: getters return by value rather than reference, which is safe but may allocate. Unit tests should assert exact names for md5, sha aliases, adler/adler32 compatibility, and padding choices.
