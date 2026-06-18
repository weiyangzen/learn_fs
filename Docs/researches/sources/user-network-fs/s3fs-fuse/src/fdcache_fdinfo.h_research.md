# sources/user-network-fs/s3fs-fuse/src/fdcache_fdinfo.h

Purpose: Declares `PseudoFdInfo`, which binds a pseudo-fd to a physical fd and records multipart upload state for that open handle.

Important APIs and types: Public APIs expose pseudo/physical fd and flags, readability/writability checks, upload-state initialization/clearing, upload id and ETag retrieval, part append, parallel multipart scheduling, pre-multipart initiation, thread waiting, boundary upload, and full-file upload/copy/download plan extraction. `fdinfo_map_t` maps pseudo-fd integers to owned `PseudoFdInfo` objects.

Control flow contract: `FdEntity` creates one `PseudoFdInfo` per open pseudo-fd and calls its upload APIs while holding entity locks where annotated. Multipart callers must initiate upload before adding parts and must collect ETags before complete.

State and persistence behavior: In-memory only. `upload_list_lock` protects all upload fields. `uploaded_sem` coordinates asynchronous worker completion. Remote multipart state is represented by `upload_id` and uploaded part metadata but is completed/aborted elsewhere.

Dependencies and integration points: Includes `fdcache_entity.h`, `psemaphore.h`, `metaheader.h`, and `types.h`; forward-declares `UntreatedParts`. It is a bridge between entity-local writes and thread-request upload APIs.

Risks: Header exposes complex planning APIs with many output lists; callers must interpret all lists consistently. Lock annotation on `UploadBoundaryLastUntreatedArea` requires the caller to hold the owning `FdEntity` mutex, tying this class to entity internals.

Test signals: Needs integration coverage for concurrent multipart, stream upload, copy-vs-upload decisions, aborted uploads, and metadata updates during upload.
