# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFile.hh

## Purpose

This header declares the `XrdSutPFile` binary credential-file API, its file-format constants, error codes, header/index record types, and public operations for reading and updating password-file entries.

## Important APIs, types, and functions

Constants define file id/version, fixed header offsets, create/open flags, and max lock tries. `EPFileErrors` enumerates internal error categories. `XrdSutPFEntInd` represents an index entry with name, next-index offset, entry offset, and entry size. `XrdSutPFHeader` represents the fixed header. `XrdSutPFile` exposes lifecycle, open/close, update, read, search, browse, and trim APIs.

## Control flow

Consumers construct or initialize a file object, then call read/write/search helpers. The class opens and closes internally for most operations unless already open, and it maintains an optional hash table to speed name lookup.

## State and persistence behavior

The declared format is persistent and offset-based. Header offsets are hard-coded constants, so file layout compatibility depends on these values and on the serialized order implemented in the source. Runtime fields track descriptor state, hash table, last hash update time, last error, and name.

## Dependencies and integration points

It depends on XRootD protocol integer types, `XrdOucHash`, `XrdOucString`, and `XrdSutPFEntry`. `XrdSutPFCache` is a friend because it needs low-level read/open/close access for cache loading.

## Risks and edge cases

The class has a copy constructor but no assignment operator, while it owns a file descriptor and heap pointers; copying can duplicate descriptor ownership unsafely. The public API uses `kXR_int32` for file offsets, limiting usable file size and assuming offset values fit 32 bits. Changing `XrdSutPFEntry::Length` or header offsets breaks compatibility with existing files.

## Test signals

Header-level compatibility tests should pin offsets, file id/version, header length, index length, and public API compile use by `XrdSutPFCache` and security admin code.
