# sources/user-network-fs/rclone/backend/premiumizeme/api/types.go

Purpose: defines Premiumize.me API response and item schemas for the backend, including uniform status handling.

Important APIs/types/functions: `Response` stores API `status` and optional `message`, implements `Error`, and `AsErr` returns nil only for `status == "success"`. `ItemTypeFolder` and `ItemTypeFile` identify item types. `Item` models files/folders with breadcrumbs, IDs, links, stream links, size, transcode status, IP, and MIME type. `Breadcrumb`, `FolderListResponse`, `FolderCreateResponse`, `FolderUploadinfoResponse`, and `AccountInfoResponse` model endpoint responses.

Control flow: only `Response.AsErr` performs active logic, converting unsuccessful decoded responses into errors. Other types are passive JSON containers.

State and persistence: no local state. Structs reflect remote folder contents, upload token/URL data, and account status/quota information.

Dependencies/integration: depends only on `fmt`. Used by the Premiumize.me backend REST layer for decoding and shared API error handling.

Risks/test signals: `AsErr` treats any status other than exact `"success"` as failure. `AccountInfoResponse` uses floats for usage fields, so callers need careful interpretation. No direct tests in this file; coverage is indirect through backend tests/integration.
