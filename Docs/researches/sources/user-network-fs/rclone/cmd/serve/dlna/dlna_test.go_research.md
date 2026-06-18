# sources/user-network-fs/rclone/cmd/serve/dlna/dlna_test.go

## Purpose

This file performs integration-style DLNA server tests against local fixture media.

## Important APIs, Types, and Functions

`startServer` creates a `server` on `localhost:0`. Tests cover initialization, root descriptor serving, content download, ContentDirectory `BrowseMetadata`, Browse response argument ordering, MediaReceiverRegistrar, direct child browsing, and RC startup.

## Control Flow

The tests start one package-level server, issue HTTP GET or SOAP POST requests, set `SOAPACTION` headers, read response bodies, and assert status codes and important XML/resource fragments. Direct-child tests browse root and subdirectories to verify subtitle URLs from same directory and `Subs`.

## State and Persistence Behavior

Tests use local fixture files and a package-global `dlnaServer`/`baseURL`. The server remains shared across tests after `TestInit`, so ordering assumptions are present.

## Dependencies and Integration Points

Dependencies include local backend registration, configfile setup, VFS, HTTP client, anacrolix SOAP, `servetest.TestRc`, and fixture media under `testdata/files`.

## Risks and Test Signals

Coverage is strong for HTTP/SOAP interoperability and Samsung-specific Browse ordering. Residual risks include test order coupling, no SSDP multicast verification, no concurrent browse/shutdown tests, and no negative SOAP malformed-request tests.
