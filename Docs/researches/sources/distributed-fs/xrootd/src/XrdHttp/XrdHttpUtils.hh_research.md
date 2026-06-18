# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.hh

Purpose: Declares common XrdHTTP utility APIs and HTTP status constants used across the HTTP core and plugins.

Important APIs/types/functions: Defines numeric constants for 1xx through 5xx HTTP statuses, `itos`, `mystrchrnul`, `calcHashes`, `compareHash`, digest/base64/hex helpers, URL `quote`/`unquote` wrappers (`decode_raw`, `encode_raw`, `encode_str`, `decode_str`), `encode_opaque`, `escapeXML`, error mapping helpers, `httpStatusToString`, and `XrdHttpIOList` as `vector<XrdOucIOVec2>`.

Control flow: Inline wrappers allocate temporary mutable buffers where required and free intermediate encoded/decoded values. `encode_opaque` splits an opaque query string on `&`, encodes key/value pairs containing `=`, and rebuilds a query body.

State and persistence: Header has no persistent state. Inline helpers allocate per call and return values or malloc-owned pointers depending on API.

Dependencies and integration points: Includes XRootD protocol, `XrdSecEntity`, `XrdOucIOVec`, `XrdOucTUtils`, and standard containers/strings. It is a central dependency for request handling, TPC, Macaroons, and response generation.

Risks: Mixed ownership conventions (`std::string` wrappers versus malloc-returned raw pointers) can leak or double-free if callers are careless. `encode_opaque` silently drops tokens without `=`, which is appropriate for key/value opaque data but may surprise callers expecting pass-through semantics.

Test signals: Compile consumers, verify constants match expected HTTP codes, test `encode_opaque` with authorization-like values, and assert mapping helpers produce expected statuses for representative errno and xrootd errors.
