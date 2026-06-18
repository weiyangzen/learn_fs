# sources/security-integrity/gocryptfs/tests/xattr/xattr_integration_test.go

## Purpose
Integration tests for encrypted extended attributes in gocryptfs, covering regular files, FIFOs, directories, empty values, large lists, base64 compatibility, permissions, ACL blobs, and names containing slashes.

## Important APIs, Types, And Functions
- `TestMain` checks xattr support, writes deterministic diriv, mounts with `-zerokey`, and tears down.
- `setGetRmList` and `setGetRmList3` implement list/set/get/remove/list assertions.
- `TestSetGetRmRegularFile`, `TestSetGetRmFifo`, `TestSetGetRmDir`, `TestXattrSetEmpty`, and `TestXattrList` cover basic operations.
- `TestBase64XattrRead` inspects encrypted backing attrs and verifies raw/base64 encrypted value decoding plus broken-data `EIO`.
- `TestList0000File`, `TestSet0200File`, `TestList0000Dir`, `TestSet0200Dir`, `TestAcl`, and `TestSlashInName` cover permissions and special names.

## Control Flow
The package mounts a deterministic encrypted-name filesystem. Tests usually operate through the plaintext mount, while `TestBase64XattrRead` also accesses the cipherdir directly using known encrypted names and attr names.

## State And Persistence
State includes xattrs on test files and directories plus a remount inside `TestBase64XattrRead` with `-wpanic=false` to tolerate intentionally malformed backing values.

## Dependencies And Integration Points
Depends on `github.com/pkg/xattr`, `internal/cryptocore`, deterministic diriv contents, and filesystem xattr/ACL support.

## Risks And Edge Cases
The deterministic encrypted names are tightly coupled to diriv and `-zerokey`. Broken backing xattrs intentionally trigger `EIO`, and ACL behavior depends on system xattr namespace support.

## Test Signals
Signals include exact value round trips, empty-list checks after removal, correct handling of nil values, expected `EIO` on malformed encrypted attr values, and permission-independent list/set behavior.
