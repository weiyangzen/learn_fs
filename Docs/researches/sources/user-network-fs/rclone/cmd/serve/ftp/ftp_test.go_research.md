# sources/user-network-fs/rclone/cmd/serve/ftp/ftp_test.go

## Purpose

This file runs rclone's generic serve tests against the FTP server.

## Important APIs, Types, and Functions

`TestFTP` defines a `start` callback for `servetest.Run`. `TestRc` verifies RC startup for FTP.

## Control Flow

The start callback configures listen host/port, passive port range, user, and password, creates a server, runs it in a goroutine, and returns a backend config for the FTP remote plus a shutdown function.

## State and Persistence Behavior

The test uses local backend fixtures managed by `servetest` and a live FTP listener on a fixed localhost port. It mutates whatever test remote `servetest` prepares.

## Dependencies and Integration Points

Build tags exclude Windows, Darwin, and Plan 9. It depends on local backend, proxy defaults, obscure password config, race-detector detection, and the generic serve test harness.

## Risks and Test Signals

The fixed port can conflict locally. Race detector skips RC due to upstream library races. Coverage is broad through generic backend tests but does not directly test TLS, auth proxy, invalid passive port parsing, or upload offsets.
