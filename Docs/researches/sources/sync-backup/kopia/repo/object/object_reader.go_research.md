# sources/sync-backup/kopia/repo/object/object_reader.go

Purpose: implements reading and verifying object data from repository content. It supports direct content objects, compressed direct objects, and recursively indirect objects whose index objects point at chunk object IDs.

Important APIs/types/functions: public `Open(ctx, r, objectID)` returns an `object.Reader`; `VerifyObject(ctx, cr, oid)` confirms all backing contents exist and returns content IDs. `objectReader` implements `Read`, `Seek`, `Close`, and `Length` over an indirect seek table. `LoadIndexObject` decodes JSON `indirectObject` entries, `newRawReader` loads direct content, and `iterateBackingContents` walks content dependencies.

Control flow: `openAndAssertLength` checks whether the ID is indirect. For indirect IDs, it loads the index object, computes total length from the last entry end offset, and returns an `objectReader`. For direct IDs, `newRawReader` gets content bytes, decompresses if the object ID has the compression flag, enforces optional asserted length, and wraps bytes in a `readerWithData`. `Read` lazily opens each chunk by recursively calling `openAndAssertLength`, reads it fully into memory, copies requested bytes, and advances chunk state. `Seek` resolves offsets through binary search on `IndirectObjectEntry.Start/endOffset`.

State and persistence behavior: reader state is transient: current overall position, chunk index, chunk bytes, and chunk-local position. Persistent state is the content manager data plus JSON index objects. `VerifyObject` persists nothing, but walks direct and indirect IDs and invokes `ContentInfo` for each backing content before adding it to a tracker.

Dependencies/integration: depends on `content.Reader`-style interfaces, `compression.DecompressByHeader`, JSON indirect object encoding from `object_writer.go`, `IndirectObjectEntry` and `Reader` definitions elsewhere in the object package, and `contentIDTracker` from the writer file.

Risks: indirect readers load each chunk fully into memory, so very large chunk sizes affect memory use. `openAndAssertLength` assumes non-empty indirect seek tables because it indexes the last entry. Invalid seek offsets below zero are not explicitly rejected before binary search. `VerifyObject` can duplicate work across repeated contents but de-duplicates return IDs through the tracker.

Test signals: object manager tests cover not-found mapping to `ErrObjectNotFound`, compressed and uncompressed reads, randomized seeks, EOF past end, length assertions through indirect chunks, and verification of backing contents.
