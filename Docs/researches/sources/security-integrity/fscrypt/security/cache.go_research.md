# sources/security-integrity/fscrypt/security/cache.go

## Purpose
`cache.go` exposes a helper to drop reclaimable inode and dentry caches so locked encrypted directories become inaccessible after key removal.

## Important APIs, Types, and Functions
`DropFilesystemCache()` is the only function.

## Control Flow
The function logs a sync step, calls `unix.Sync`, opens `/proc/sys/vm/drop_caches` with write and sync flags, writes `"2"`, and returns any open or write error.

## State and Persistence
It changes kernel VM cache state and requires root privileges. It does not persist repository or fscrypt metadata state.

## Dependencies and Integration Points
Uses `golang.org/x/sys/unix`, `os`, and `log`. `pam_fscrypt.CloseSession` calls it when deprovisioning user-keyring policies requires cache dropping to complete locking.

## Risks
Requires root and access to procfs. Dropping dentries/inodes can affect system performance, though it avoids dropping the entire page cache. It assumes cache dropping is needed only in specific legacy/user-keyring cases.

## Test Signals
No direct behavioral tests beyond package stub. Root-only integration would be required to validate actual cache dropping.
