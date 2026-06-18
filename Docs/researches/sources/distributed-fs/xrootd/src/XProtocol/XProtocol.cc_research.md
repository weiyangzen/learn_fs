# sources/distributed-fs/xrootd/src/XProtocol/XProtocol.cc

## Purpose
This source implements helper routines for XRootD protocol names and file-attribute vector encoding/decoding.

## Important APIs, Types, and Functions
Static tables map XRootD error codes to messages (`errNames`) and request codes to names (`reqNames`). `XProtocol::errName` and `XProtocol::reqName` normalize possible network-byte-order values and return stable strings. `ClientFattrRequest::NVecInsert`, `VVecInsert`, `NVecRead`, and `VVecRead` write/read name-vector and value-vector records for file attribute protocol payloads.

## Control Flow
Error/request name lookups first byte-swap values on little-endian hosts when values are outside the expected host-order range, validate bounds against protocol fences, and return fallback strings for unknown values. Vector insert functions append encoded fields into caller-provided buffers. Vector read functions extract status/name/value fields from buffers, allocating copied strings for names/values where needed.

## State and Persistence
The file has immutable lookup tables and a static endianness probe. It does not persist data; it serializes/deserializes protocol payload fragments in memory. `NVecRead` uses `strdup` and `VVecRead` uses `malloc`, transferring allocation cleanup responsibility to callers.

## Dependencies and Integration Points
Depends on `XProtocol/XProtocol.hh`, C/POSIX headers, byte-order functions, and protocol constants such as `kXR_ArgInvalid`, `kXR_ERRFENCE`, `kXR_auth`, and `kXR_REQFENCE`. Built into `XrdUtils`.

## Risks and Test Signals
Comments say "byte orderdoesn't" and code uses `htons`/`htonl` while reading where `ntohs`/`ntohl` would be clearer; round-trip tests are important. Insert functions assume caller buffers are sufficiently large. Read functions allocate memory that callers must free. Tests should cover host-order and network-order code lookups, unknown/fence values, nvec/vvec round trips, empty strings, long values, and allocation cleanup.
