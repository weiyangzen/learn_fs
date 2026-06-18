# sources/object-store/minio-mc/cmd/share.go

## Purpose
Provides common constants, flags, message formatting, color setup, and local config-file helpers for share upload/download/list commands.

## Important APIs, types, and functions
- `shareDefaultExpiry` is 7 days.
- `shareFlagContentType` and `shareFlagExpire` are shared CLI flags.
- `shareMessage` is the common output type for object URL, share URL, time left, and optional content type.
- `shareMessage.String` prints text output and highlights `<FILE>` and `<NAME>` placeholders.
- `shareMessage.JSON` marshals JSON and unescapes `&`, `<`, and `>` for usable share URLs/templates.
- `shareSetColor` configures console themes.
- `getShareDir`, `mustGetShareDir`, `createShareDir`, `getShareUploadsFile`, `getShareDownloadsFile`, and existence helpers manage local paths.
- `initShareConfig` creates the share directory and empty upload/download DBs.

## Control flow
Subcommands call `initShareConfig` before reading or writing share DBs. It creates the share directory with mode `0700`, initializes `uploads.json` and `downloads.json` using `newShareDBV1().Save`, and prints informational messages unless quiet/JSON mode is active. `shareMessage` handles both text and JSON output paths through the global `message` interface.

## State and persistence
Creates and maintains local files under the mc config directory's shared URLs data directory: `uploads.json` and `downloads.json`. It does not itself add share entries; command files do that through `shareDBV1`.

## Dependencies and integration points
Uses config path helpers (`getMcConfigDir`), global constants (`globalSharedURLsDataDir`), `quick` through DB initialization, console color, global quiet/JSON flags, and `probe.Error`.

## Risks and edge cases
- `mustGetShareDir` fatal-exits on config path errors, so many helper calls can terminate the command.
- JSON output intentionally reverses Go's HTML escaping for generated URLs and placeholders.
- Directory mode is restrictive, but file permissions are controlled by `quick.Save`.

## Test signals
No direct tests in this subset. Tests should cover config initialization, JSON unescaping, placeholder highlighting, and quiet/JSON suppression of init messages.
