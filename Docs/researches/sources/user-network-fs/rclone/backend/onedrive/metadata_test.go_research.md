# sources/user-network-fs/rclone/backend/onedrive/metadata_test.go

## Purpose
`metadata_test.go` unit-tests the permission ordering workaround in OneDrive metadata handling. The ordering places permissions involving users before group-only permissions to avoid a Microsoft Graph behavior where adding a group before an equivalent user permission can cause the user permission to be dropped.

## Important APIs, Types, And Functions
`TestOrderPermissions` defines table-driven inputs of `*api.PermissionsType` and expected ID order. It runs each case for `driveTypePersonal` and `driveTypeBusiness`, converting personal fields to V2 business fields for the latter. `TestOrderPermissionsJSON` unmarshals a business-style JSON permissions array and verifies user-before-group ordering. Both tests call `Metadata.orderPermissions`.

## Control Flow
For each case, the test constructs a minimal `Metadata{fs: &Fs{driveType: ...}}`, applies the ordering in place, collects permission IDs, and compares them with the expected stable order. Cases cover empty input, mixed user/group/none, same-type stability, all-user stability, and missing identity data.

## State And Persistence Behavior
The tests are pure unit tests. They allocate permission slices in memory and perform no Graph calls or filesystem operations.

## Dependencies And Integration Points
The file imports `encoding/json`, the OneDrive `api` package, and `testify` assertions. It directly exercises an unexported method because it is in package `onedrive`.

## Risks And Edge Cases
The table mutates `tt.input` when converting to business fields, but each subtest instance is scoped under the drive type loop and the personal run happens before business in the literal slice order. Future parallelization or reuse could make that mutation surprising. The tests do not cover `sortPermissions`, recipient filling, anonymous links, owner protection, or failok behavior.

## Test Signals
Passing tests confirm the Graph workaround preserves relative order except for moving any user-bearing permission ahead of non-user permissions and handles both personal and business identity field variants.
