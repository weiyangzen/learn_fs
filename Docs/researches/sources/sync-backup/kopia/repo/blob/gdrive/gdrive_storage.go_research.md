# sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage.go

Purpose: implements Kopia blob storage on Google Drive files in a configured folder.

Important APIs/types/functions: `gdriveStorage`, `GetCapacity`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `FlushCaches`, file-ID lookup helpers, prefix/range/name helpers, metadata parsing, `translateError`, credential token-source helpers, `CreateDriveService`, `New`, and provider `init`.

Control flow: capacity reads Drive quota. Reads resolve blob ID to Drive file ID through the cache/API, set an HTTP Range header, download, copy non-zero bodies, and verify exact length. Metadata lookup uses cache, falls back to Drive queries, fetches full metadata when needed, and parses modified time. Writes reject retention, resolve existing file ID, enforce `DoNotRecreate`, create or update a Drive file with media upload and optional modified time, update cache/change log, and return mod time. Deletes resolve file ID, delete it, clear cache entry, and record deletion. Listing queries files in the folder by MIME type and optionally capped name `contains` prefix, updates cache, filters exact prefix client-side, and uses recent cache changes to include blobs the Drive list missed. `New` warns about risk, creates Drive service using raw/file/default credentials, verifies listing, and wraps in retrying.

State and persistence behavior: each blob is a Drive file with name equal to blob ID and MIME `application/x-kopia`. File ID cache is transient; blob contents/mtimes persist in Drive.

Dependencies/integration points: uses Google Drive v3 API, OAuth2/JWT credentials, retry helpers, file ID cache, and storage registry. Risks include Drive search not supporting long prefix matches, eventual consistency, duplicate files causing hard errors, no retention support, fixed upload chunk size, default HTTP client behavior, and provider not actively tested. Tests cover cleanup, shared behavior, and invalid setup with live Drive.
