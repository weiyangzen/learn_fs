# sources/user-network-fs/rclone/fs/operations/operations_internal_test.go

## Purpose
`operations_internal_test.go` provides package-internal coverage for helpers that are not exported, currently focused on `sizeDiffers`.

## Important APIs, types, and functions
- `TestSizeDiffers` builds static object infos and tests `sizeDiffers` across ignore-size and unknown-size combinations.

## Control flow
The test iterates table cases with source size, destination size, `IgnoreSize`, and expected result. For each case it creates `object.NewStaticObjectInfo` values, temporarily mutates `ci.IgnoreSize`, calls `sizeDiffers`, restores the old config value, and asserts the result.

## State and persistence behavior
No remote state is created. The only state mutation is the temporary global config field `IgnoreSize`, restored after each case.

## Dependencies and integration points
The file uses the internal `operations` package, `fs.GetConfig`, `object.NewStaticObjectInfo`, `time`, and `testify`. It directly tests a helper that affects `Equal`, `Check`, `Copy.verify`, and transfer decisions.

## Risks and edge cases
Unknown sizes (`-1`) should not be treated as differing, and `--ignore-size` must suppress mismatches entirely. Because config is process-global for the context, restoration is essential to avoid contaminating later tests.

## Test signals
The test confirms exact equal sizes return false, positive mismatched known sizes return true, unknown source or destination sizes return false, and ignore-size forces false regardless of sizes.
