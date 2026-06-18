# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.cc

## Purpose

This file implements conversion from Metalink XML v3 or v4 documents into one or more `XrdOucFileInfo` objects. It extracts file names, URLs, hashes, sizes, global logical file names, priorities, and protocols while allowing callers to filter URL protocols and optionally synthesize a global redirect URL.

## Important APIs, Types, and Functions

- `XrdXmlMetaLink::Convert(const char *fname, int blen)`: converts the first applicable file entry from a path or memory buffer.
- `XrdXmlMetaLink::ConvertAll(const char *fname, int &count, int blen)`: converts all file entries and returns an array of `XrdOucFileInfo *`.
- `XrdXmlMetaLink::DeleteAll`: deletes arrays returned by `ConvertAll`.
- Private parsing helpers: `GetFile`, `GetFileInfo`, `GetGLfn`, `GetHash`, `GetSize`, `GetUrl`, `GetName`, `UrlOK`, `GetRdrError`, and `PutFile`.
- RAII helper classes `CleanUp` and `vecMon`: delete the active reader/temp file and free attribute vectors.

## Control Flow

For buffer input, `PutFile` writes the buffer to a unique `/tmp/.MetaLink<time>.<pid>.<seq>` path, then cleanup unlinks it on return. `Convert` creates an `XrdXmlReader`, finds the root `metalink` tag, reads its `xmlns`, switches v3 documents into the `files` scope, and rejects unknown namespaces. It then loops over `file` tags, allocating a new `XrdOucFileInfo`, extracting sub-elements, linking successful entries into `fileList`, and optionally adding a global URL constructed from `rdProt`, `rdHost`, and an extracted `glfn`. In single-file mode it returns only the first linked file and treats accumulated errors as fatal.

`GetFileInfo` walks selected child tags in the current scope. `url` tags add matching protocol URLs and set `noUrl=false`; `hash` and `size` are required to contain valid text when encountered; `verification` and `resources` are processed recursively; `glfn` adds an LFN. The final result for a file is accepted only if at least one URL passed the protocol filter.

## State and Persistence Behavior

Each `XrdXmlMetaLink` instance keeps parser state in `reader`, `fileList`, `lastFile`, `currFile`, `fileCnt`, `doAll`, `noUrl`, and last error fields `eCode/eText`. Temporary file naming uses process-wide `tmpPath`, `seqNo`, and `xMutex`, seeded by `GenTmpPath`. Temporary files are persisted only during conversion and unlinked by `CleanUp`.

## Dependencies and Integration Points

The converter depends on `XrdXmlReader` implementations, `XrdOucFileInfo` mutators (`AddUrl`, `AddProtocol`, `AddDigest`, `SetSize`, `AddLfn`, `AddFileName`), XRootD atomics/mutex wrappers, `XrdSysFD_Open`, `XrdSysE2T`, and POSIX `unlink`, `write`, and `close`. It is the consumer-facing bridge from XML metalink documents to XRootD file-location metadata.

## Risks

- `ConvertAll` sets `doAll=true` and never resets it, so reusing the same object for later `Convert` calls can keep all-file behavior.
- The temporary-file implementation uses `/tmp` and a custom name scheme rather than `mkstemp`; `O_EXCL` helps but failure paths and permissions still need scrutiny.
- `UrlOK` records every protocol on the `XrdOucFileInfo` before checking the filter, so rejected protocols can still appear in protocol metadata.
- `strstr(prots, pBuff)` can match protocols as substrings if protocol-list formatting is not strict.
- XML content is accepted leniently; the header comment explicitly says it is not a rigorous RFC validator.
- In `PutFile`, `fd > 0` treats descriptor 0 as failure even though `open` can legally return 0.

## Test Signals

Tests should cover Metalink v3 and v4 root namespace handling, required `xmlns`, unsupported namespace rejection, URL protocol filtering, v3 `files` scoping, nested `verification/resources`, invalid sizes, missing hash attributes, buffer input cleanup, `ConvertAll` array ownership, and global URL synthesis from `glfn`.
