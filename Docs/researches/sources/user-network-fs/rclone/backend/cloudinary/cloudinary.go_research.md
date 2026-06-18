# sources/user-network-fs/rclone/backend/cloudinary/cloudinary.go

## Purpose
This file implements the `cloudinary` rclone backend, exposing Cloudinary Digital Asset Management as an `fs.Fs` with object listing, lookup, upload, update, download, directory creation/removal, hashing, and eventual-consistency handling. It registers configuration for Cloudinary credentials, upload prefix/preset, path encoding, consistency delay, and Cloudinary media extension adjustment.

## Important APIs, types, and functions
`Options` stores Cloudinary credentials and behavior flags. `Fs` holds rclone identity, root, options, feature set, pacer, CDN REST client, Cloudinary SDK client, and `lastCRUD`. `Object` stores rclone-visible metadata plus Cloudinary `publicID`, resource type, delivery type, URL, MD5/etag, and timestamps. `NewFs` builds SDK clients with rclone HTTP clients, applies upload prefix, initializes the pacer and features, and detects whether the configured root points at a file. Encoding helpers bridge rclone names and Cloudinary's path/display conventions: `FromStandardPath`, `FromStandardName`, `ToStandardPath`, `ToStandardName`, `FromStandardFullPath`, `ToAssetFolderAPI`, and `ToDisplayNameElastic`.

Core filesystem methods are `List`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Hashes`, `Precision`, and feature accessors. Object methods implement hash, metadata accessors, `Open`, `Update`, and `Remove`. `shouldRetry` centralizes retry handling for context cancellation, HTTP retry codes, general retryable errors, and Cloudinary rate-limit messages containing retry timestamps.

## Control flow
`List` first lists subfolders with `Admin.SubFolders`, then assets with `Admin.AssetsByAssetFolder`, converting Cloudinary folder/display names back to rclone paths and appending directories and objects. `NewObject` uses Cloudinary Admin Search against `asset_folder` and escaped `display_name`, sorts newest first, retries partial responses through the pacer, and materializes the first result. `Put` builds `uploader.UploadParams`; update mode is activated by backend-specific `api.UpdateOptions`, otherwise it derives asset folder and display name from the source remote and suggests a deterministic BLAKE3 public ID. `Open` performs a CDN GET through `rest.Client`, translates range/seek options into headers, and retries until returned content length matches the expected range count.

## State and persistence behavior
Persistent state lives in Cloudinary assets and folders. The backend maintains only local connection/client state plus `lastCRUD`, used by `WaitEventuallyConsistent` to sleep after CRUD operations when configured. Object identity is stored as Cloudinary `publicID` plus resource/delivery type, while rclone-visible paths are reconstructed from Cloudinary asset folders and display names. Empty files cannot be uploaded. Modtime precision is unsupported; update paths set local object modtime to `time.Now()` because Cloudinary returns creation time for overwritten assets.

## Dependencies and integration points
The file integrates rclone `fs`, config, HTTP, hashing, pacer, REST, encoder, and Cloudinary-specific API helpers. Cloudinary operations go through `github.com/cloudinary/cloudinary-go/v2` Admin and Upload SDKs; CDN downloads use rclone's `rest.Client`. Name handling depends on `backend/cloudinary/api.CloudinaryEncoder`. The backend declares empty-directory support and MD5 hashes.

## Risks and edge cases
Cloudinary media extension adjustment strips or reattaches extensions based on URL and configured media extensions, which can affect names with query strings or uncommon extensions. Search selects the first of up to two newest matching assets, so duplicate display names depend on Cloudinary ordering. `List` reuses `nextCursor` between the folder and asset phases without resetting it, which deserves scrutiny if folder listing returns a cursor before completion. `shouldRetry` slices retry-after text assuming the full timestamp length is present; malformed messages could panic. CDN range validation depends on `content-length` matching `count`, but `count` may be zero when no range option is supplied, causing normal whole-file downloads to rely on retry semantics.

## Test signals
Coverage is mainly integration-driven by `cloudinary_test.go`, which runs rclone `fstests` against a configured Cloudinary remote with a 7-second eventual-consistency delay and invalid UTF-8 skipped. There are no local unit tests for encoding helpers, retry parsing, or the folder/assets pagination flow.
