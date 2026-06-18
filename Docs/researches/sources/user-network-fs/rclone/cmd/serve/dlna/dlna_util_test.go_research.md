# sources/user-network-fs/rclone/cmd/serve/dlna/dlna_util_test.go

## Purpose

This test file protects DLNA XML compatibility normalization.

## Important APIs, Types, and Functions

`TestAdjustXML` calls `adjustXML` with simple, quoted, mixed, already-normalized, and nested XML strings.

## Control Flow

Each subtest compares the returned string to an expected value, ensuring numeric quote entities become `&quot;` while already named entities are preserved.

## State and Persistence Behavior

No persistent state is touched.

## Dependencies and Integration Points

It depends only on `testing`, testify assertions, and the helper under test.

## Risks and Test Signals

It is a precise regression signal for Samsung-compatible entity output. It does not test apostrophes and all "Big 5" entities because those cases live in `cds_test.go`.
