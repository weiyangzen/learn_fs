<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server.go -->
# sources/object-store/minio/cmd/ftp-server.go

## Purpose
Starts and configures the optional FTP/FTPS server front-end for MinIO. It parses `--ftp` key-value arguments, configures TLS and passive mode, and launches a goftp server backed by `ftpDriver`.

## Important APIs, types, and functions
- `globalRemoteFTPClientTransport` is the HTTP transport used by FTP driver clients.
- `minioLogger` implements goftp logging methods while masking PASS commands and honoring `serverDebugLog`.
- `startFTPServer` parses address, passive port range, TLS key/cert, and force-TLS settings; creates the server; and calls `ListenAndServe`.

## Control flow
Arguments are split as `key=value` and validated. Address parsing enforces a numeric port between 1 and 65535, with default 8021. TLS key/cert must be supplied together; if MinIO's S3 API is already TLS-enabled and FTP TLS files are not provided, it reuses MinIO cert files. `force-tls` requires TLS to be configured. The server is then created with welcome text, `NewFTPDriver`, simple permissions, passive/public IP options, explicit FTPS, logger, and TLS settings.

## State and persistence behavior
This file creates a long-running listener; it does not persist data itself. Data operations are handled by `ftp-server-driver.go`. Startup failures call `logger.Fatal`, terminating the process.

## Dependencies and integration points
Depends on goftp server options, MinIO global TLS/cert settings, version/license constants, FTP driver, and logger. It integrates with command-line server startup and optional S3 TLS configuration.

## Risks and edge cases
Invalid or partial TLS inputs are fatal. Reusing S3 TLS certs assumes those files are usable for FTP. Unknown argument keys are ignored by the switch, which can hide typos. The listener blocks in `ListenAndServe` and must be launched from an appropriate goroutine by caller code.

## Test signals
No direct tests in this group. Operational signals are successful listener startup, fatal validation for malformed args, PASS masking in debug logs, and FTPS behavior under explicit/forced TLS.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/ftp-server.go -->
