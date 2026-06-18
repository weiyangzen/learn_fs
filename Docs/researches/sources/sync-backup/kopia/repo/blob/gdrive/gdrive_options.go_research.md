# sources/sync-backup/kopia/repo/blob/gdrive/gdrive_options.go

Purpose: defines persistent options for Google Drive-backed blob storage.

Important APIs/types/functions: `Options` with folder ID, credentials file or raw JSON, read-only flag, and throttling limits. The file is behind `!no_extra_providers`.

Control flow: no functions are defined here. Client creation and validation occur in `gdrive_storage.go`.

State and persistence behavior: the struct is serialized in repository connection config. Raw credential JSON is marked sensitive. The folder ID is the persistent namespace root for blob files.

Dependencies/integration points: consumed by GDrive provider creation and config round-tripping. Risks include provider warning that it is not actively tested and may cause data loss, Drive API limitations around prefix search, and read-only being enforced through OAuth scope rather than wrapper-level mutation blocking. Live tests cover basic behavior when credentials/folder are configured.
