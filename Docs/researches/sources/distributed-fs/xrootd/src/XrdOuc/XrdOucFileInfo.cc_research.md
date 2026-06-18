# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.cc

## Purpose
Implements `XrdOucFileInfo`, a description of a logical file, target file name, size, available protocol names, ordered URLs, and validation digests.

## Important APIs, Types, And Functions
Private helper classes `XrdOucFIHash` and `XrdOucFIUrl` store linked-list digest and URL entries. `XrdOucFIHash::XrdhName` maps Adler variants to XRootD digest name `a32`. Implemented methods add digests, URLs, filenames, logical filenames, protocols, and iterate digests/URLs with `GetDigest`/`GetUrl`.

## Control Flow
`AddDigest` prepends a lowercase digest name/value and resets digest iteration to the new head. `AddUrl` inserts by increasing priority; with `fifo=true`, equal priority entries are appended, otherwise inserted before equal priority entries. `GetDigest` and `GetUrl` are stateful iterators: returning null resets the next pointer to the head for a future pass.

## State And Persistence
All state is in-memory and owned by the object: linked digest nodes, linked URL nodes, duplicated LFN/target strings, file size, and a concatenated protocol string. Destructor frees all owned allocations.

## Dependencies And Integration Points
Depends on `XrdOucFileInfo.hh` and C allocation/string APIs. It integrates with redirect/discovery code that reports multiple file locations and checksums to clients.

## Risks And Test Signals
Risks include no locking, stateful iterators that reset only after an end-of-list call, protocol membership via substring search on concatenated names, no URL/digest allocation failure handling, and potential `strncpy(user)`-style assumptions in consumers of returned country codes. Test signals include URL priority/FIFO ordering, digest name normalization, iterator reset behavior, target/LFN replacement, and protocol false-positive cases such as overlapping protocol names.
