# sources/user-network-fs/rclone/cmd/serve/http/http_test.go

## Purpose

This file regression-tests the HTTP server against golden directory listings, file bodies, ranges, zip downloads, favicon behavior, compression, auth proxy, and RC setup.

## Important APIs, Types, and Functions

Helpers include `start`, `setAllModTimes`, `checkGolden`, and `testGET`. Tests include `TestGET`, `TestAuthProxy`, `TestFavicon`, `TestCompressedDirectoryListing`, `TestCompressedTextFile`, and `TestRc`.

## Control Flow

The main GET test configures filters, starts a local server with basic auth or proxy auth, sends requests with expected methods/ranges, validates status and Last-Modified headers, and compares bodies to golden files. Favicon tests verify embedded fallback and remote override. Compression tests request gzip and decompress the response.

## State and Persistence Behavior

Tests mutate fixture file mtimes and optionally update golden files when `-updategolden` is set. Servers and temp proxy processes are scoped to tests.

## Dependencies and Integration Points

They depend on local backend, filter config, lib/http defaults, proxy test code, VFS defaults, golden files, and `servetest.TestRc`.

## Risks and Test Signals

Golden files give strong regression coverage but can be brittle across template changes. Coverage includes many user-visible paths; residual gaps include unknown-size objects, zip errors during streaming, custom template parsing failures, and concurrent shutdown.
