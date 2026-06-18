
# sources/user-network-fs/rclone/backend/http/http_internal_test.go

## Purpose
This file provides unit and integration-style tests for the HTTP backend using a local `httptest` server and static fixture files/listings.

## Important APIs, Types, And Control Flow
`prepareServer` serves fixture files, asserts configured headers on requests, injects metadata headers for `five.txt.gz`, and returns a config map. Tests cover root listing with and without `NoSlash`, subdirectory listing, object stat with and without leading slash, metadata extraction, normal and range reads with and without HEAD, MIME type, root paths that point to files, `parseName`, HTML parser fixtures for Apache/Memstore/Nginx/Caddy, and `getFsEndpoint` behavior across HEAD status and redirect cases.

## State And Persistence
Tests use local fixture files under `test/files` and `test/index_files`, local HTTP test servers, and temporary in-memory config. They do not mutate external remotes.

## Dependencies And Integration Points
The tests import rclone config and fstest helpers, `httptest`, local fixtures, and `testify`. They exercise unexported package functions because they are in package `http`.

## Risks And Test Signals
The tests provide strong signals for parsing, header injection, metadata, range reads, and root classification. They do not cover the backend `set` command, read-only method errors, no-escape path behavior, malformed `Content-Disposition`, concurrent `List` failure races, or HTTP status handling beyond selected root HEAD paths.
