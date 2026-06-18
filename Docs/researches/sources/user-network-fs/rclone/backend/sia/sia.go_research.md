# sources/user-network-fs/rclone/backend/sia/sia.go

## Purpose

`sia.go` implements rclone support for Sia decentralized cloud storage via a local or remote `siad` HTTP API.

## Important APIs, Types, and Functions

`Options` stores API URL, API password, user agent, and path encoder. `Fs` owns remote identity, root prefix, REST client, feature set, and pacer. `Object` stores remote path, modtime, and size. Major methods include `NewFs`, `List`, `NewObject`, `Put`, `PutStream`, `Mkdir`, `Rmdir`, object `Open`, `Update`, `Remove`, `readMetaData`, `errorHandler`, and `shouldRetry`.

## Control Flow

Initialization trims and parses `api_url`, configures an HTTP client with the Sia user agent, installs basic auth when `api_password` is present, and detects root-as-file when the root does not end with `/`. Reads use `/renter/stream/<path>` with rclone range options. Writes use `/renter/uploadstream/<path>?force=true`, then refresh metadata. Listing calls `/renter/dir/<prefix>/`, skips the directory itself, and converts returned directories/files to rclone entries. `Rmdir` first lists the target to confirm existence and emptiness, then posts `action=delete`.

## State and Persistence Behavior

The backend keeps only in-memory metadata and connection state. Persistence is on the Sia daemon side: uploaded streams become renter files, directory creation/deletion uses Sia renter state, and config may contain an obscured API password.

## Dependencies and Integration Points

It integrates rclone `fs`, `fshttp`, `rest`, `pacer`, `encoder`, and `obscure` with Sia renter endpoints. It exposes empty-directory support and streaming uploads, but no hashes and no settable modtime.

## Risks and Edge Cases

`errorHandler` relies on string matching because Sia errors are not structured with stable codes. `shouldRetry` only checks generic errors, not HTTP status retry codes. `Put` performs best-effort cleanup after failed upload with fixed retries. Empty-file range reads drop a problematic range option. The API security note warns that exposing siad remotely with disabled API security is unsafe.

## Test Signals

`sia_test.go` runs rclone's integration suite against `TestSia:`. Additional useful tests would mock Sia error messages, root-as-file detection, failed-upload cleanup, empty-file ranged opens, and empty/non-empty directory removal.
