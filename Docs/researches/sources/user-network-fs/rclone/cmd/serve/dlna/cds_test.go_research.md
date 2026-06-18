# sources/user-network-fs/rclone/cmd/serve/dlna/cds_test.go

## Purpose

This file unit-tests ContentDirectory helper behavior that is difficult to verify only through full DLNA server requests.

## Important APIs, Types, and Functions

`TestMediaWithResources` builds a local backend VFS and calls `mediaWithResources`. `TestSOAPResponseQuoteEscaping`, `TestTitleExtensionRemoval`, and `TestAdjustXMLApostrophes` validate output formatting expectations.

## Control Flow

The tests list fixture directories, append `Subs` entries where needed, and assert that media nodes retain matching `.srt`, language-suffixed `.srt`, and `.idx`/`.sub` resources. Formatting tests simulate marshaled SOAP/DIDL payloads and verify named XML entities and extension-trimmed titles.

## State and Persistence Behavior

Tests use local fixture files and in-memory VFS nodes. They do not mutate persistent source fixtures.

## Dependencies and Integration Points

They depend on the local backend, VFS, anacrolix SOAP args, testify, and `cmd/serve/dlna/testdata/files`.

## Risks and Test Signals

The tests are strong signals for DLNA client compatibility fixes, especially Samsung behavior. They do not cover malformed ObjectIDs, huge directories, MIME fallback failures, browse pagination edge cases beyond the implementation path, or actual XML schema validation.
