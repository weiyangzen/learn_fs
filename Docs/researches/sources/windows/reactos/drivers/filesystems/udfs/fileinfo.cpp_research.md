# File Research: sources/windows/reactos/drivers/filesystems/udfs/fileinfo.cpp

`fileinfo.cpp` implements `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION` for UDFS file objects. It is the central bridge between NT file-information classes and UDF in-memory/on-disk metadata: timestamps, attributes, sizes, stream information, delete-on-close, rename/move, optional hard links, and file-ID reopen support.

Primary dispatch flow:
- `UDFFileInfo()` establishes filesystem/top-level IRP context and calls `UDFCommonFileInfo()`.
- `UDFCommonFileInfo()` validates `Ccb`/`Fcb`, rejects VCB-as-file queries, acquires the VCB shared, and dispatches query or set information classes.
- Query classes handled include `FileBasicInformation`, `FileStandardInformation`, `FileNetworkOpenInformation`, `FileInternalInformation`, `FileEaInformation`, `FileNameInformation`, `FileAlternateNameInformation`, `FilePositionInformation`, `FileStreamInformation`, and `FileAllInformation`.
- Set classes handled in writable builds include `FileBasicInformation`, `FilePositionInformation`, `FileDispositionInformation`, `FileRenameInformation`, optional `FileLinkInformation`, `FileAllocationInformation`, and `FileEndOfFileInformation`.

Query helpers:
- `UDFGetBasicInformation()` copies cached FCB times, updates directory-index time caches, composes NT attributes, and honors `FO_TEMPORARY_FILE`.
- `UDFGetStandardInformation()` reports link count, delete-pending state, directory flag, allocation size, and EOF.
- `UDFGetNetworkInformation()` combines basic timestamps, size/allocation fields, and attributes for network-open queries.
- `UDFGetInternalInformation()` computes a UDF-backed NT file ID and stores a path mapping in the VCB file-ID cache.
- `UDFGetEaInformation()` reports zero EA size.
- `UDFGetFullNameInformation()` returns `FileObject->FileName`; `UDFGetAltNameInformation()` synthesizes an 8.3/DOS name.
- `UDFGetFileStreamInformation()` walks the stream directory index and emits `FILE_STREAM_INFORMATION` records for non-deleted, non-internal streams.

Set and mutation helpers:
- `UDFSetBasicInformation()` updates UDF timestamps, FCB time caches, NT/UDF attributes, read-only and temporary flags, archive-related state, and directory-change notifications.
- `UDFSetDispositionInformation()` enforces read-only/root/non-empty/mapped-image checks, marks or unmarks delete-on-close, and delegates stream-tree marking to `UDFMarkStreamsForDeletion()`.
- `UDFMarkStreamsForDeletion()` opens the stream directory, validates image sections with `MmFlushImageSection()`, and recursively marks streams and stream directories with `UDF_FCB_DELETE_ON_CLOSE`/`UDF_FCB_DELETE_PARENT`.
- `UDFSetAllocationInformation()` and `UDFSetEOF()` coordinate file growth/truncation with free-space checks, `MmCanFileBeTruncated()`, `UDFResizeFile__()`, `PagingIoResource`, `CcSetFileSizes()`, archive-bit updates, and notify-change events.
- `UDFPrepareForRenameMoveLink()` converts VCB/resource ownership to a deadlock-avoiding state before rename/move/hard-link operations.
- `UDFRename()` validates source/target directories, stream-directory restrictions, open-reference safety, name length, replacement rules, performs `UDFRenameMoveFile__()`, updates parent/file references and FCB names, and emits remove/add/rename notifications.
- `UDFHardLink()` is compiled only with `UDF_ALLOW_HARD_LINKS`; it uses similar validation and notification logic around `UDFHardLinkFile__()`.

File-ID cache:
- `UDFFindFileId()`, `UDFFindFreeFileId()`, `UDFStoreFileId()`, `UDFRemoveFileId()`, `UDFReleaseFileIdCache()`, and `UDFGetOpenParamsByFileId()` maintain a VCB-side mapping from generated file IDs to full names and case-sensitivity state.

Notable behavior and dependencies:
- The file is highly synchronization-sensitive: VCB, parent FCB, current FCB, and paging resources are acquired differently for query, position-only set, rename/link, page-file mutation, and size-changing requests.
- Size updates intentionally handle recursive Cache Manager callbacks by using `AcqFlushCount`, temporary cache-map initialization, and `CcSetFileSizes()`.
- Many write paths are compiled out under `UDF_READ_ONLY_BUILD`.
- Rename/move code has extensive reference-count repair for CCB path chains when moving across directories.
