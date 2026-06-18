# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/mock_read_manager.go

## Scope

This file defines a testify mock implementation of `gcsx.ReadManager` for read-manager wrapper tests.

## Purpose

`MockReadManager` lets tests assert delegation from wrappers such as `VisualReadManager` without constructing real GCS/cache readers.

## Important APIs, Types, And Functions

- `MockReadManager` embeds `gcsx.ReadManager` and `mock.Mock`.
- `ReaderName` returns `mock_read_manager`.
- `ReadAt`, `Object`, `Destroy`, and `CheckInvariants` dispatch to testify `Called`.

## Control Flow

Each mocked method records and returns configured expectations. `ReadAt` type-asserts the first return value to `gcsx.ReadResponse`; `Object` type-asserts to `*gcs.MinObject`.

## State And Persistence Behavior

No production state is stored beyond testify mock call history and configured return values.

## Dependencies And Integration Points

It depends on `context`, `gcsx` reader contracts, `gcs.MinObject`, and `stretchr/testify/mock`. It is used by `visual_read_manager_test.go`.

## Risks And Maintenance Notes

Tests must configure all methods that will be called; otherwise testify will fail or type assertions can panic if return slots are missing or nil. If `ReadManager` grows new required methods, this mock must be updated.

## Test Signals

The file itself has no direct tests, but `visual_read_manager_test.go` exercises its method expectations for `Object`, `ReadAt`, and `Destroy`.
