<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/logger.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/logger.go

Source read: complete file, 35 lines, 565 bytes, sha256 `f752935f50404f9f2f2fc7e92cc2d0d5d059c30dfea32db41f6855739ec11e3e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/logger.go_research.md`.

## Purpose
Adapts gofakes3 logging into rclone's fs logging levels.

## Important APIs, types, and functions
`logger.Print` joins variadic values into one string and maps error, warning, and info levels to `fs.Errorf`, `fs.Infof`, and `fs.Debugf`.

## Control flow
The server passes this logger when constructing `gofakes3.GoFakeS3`.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends on `gofakes3.LogLevel` and rclone `fs` logging.

## Risks and edge cases
Level mapping is intentionally compressed; gofakes3 info becomes debug, so normal verbosity may hide request details.

## Test signals
Covered indirectly whenever S3 server tests emit gofakes3 logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/logger.go -->
