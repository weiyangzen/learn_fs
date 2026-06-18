# sources/test-tools/syzkaller/pkg/asset/storage_test.go

## Purpose
Comprehensive tests for asset storage upload, compression, dashboard reporting, duplicate handling, and deprecation.

## Important APIs, Types, and Functions
Defines `dashMock`, `makeStorage`, `collectBytes`, `validateGzip`, `validateXz`, and helper `sendBuildAsset`. Tests cover build assets, HTML assets, recent deletion protection, configuration, same-content upload, two-bucket deprecation, and invalid URLs.

## Control Flow
Tests use dummy backend callbacks to capture compressed bytes, upload assets through public methods, report them to a mock dashboard, manipulate needed URL sets, and run `DeprecateAssets` under success/error scenarios.

## State and Persistence Behavior
All state is in-memory dummy backend maps and mock dashboard URL maps. Time is controlled through `be.currentTime` for embargo behavior.

## Dependencies and Integration Points
Validates xz/gzip compressor wrappers, dummy backend URL mapping, dashboard API contract, and storage deprecation safety checks.

## Risks and Test Signals
Strong signal for storage behavior without real GCS. It does not cover cloud writer failures or concurrent upload/delete races.
