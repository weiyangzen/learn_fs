<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find_research.md`. Source lines read for this pass: 59.

## Purpose
Shell utility that maps between encrypted and decrypted eCryptfs pathnames by using inode numbers across current eCryptfs mounts.

## Important APIs, Types, And Functions
No functions; command-line argument `$1`, `/proc/mounts`, `ls -aid`, `awk`, and `find -inum` are the operative interfaces.

## Control Flow
Validates the supplied path, infers encrypt or decrypt direction by whether the name contains `ECRYPTFS_FNEK_ENCRYPTED.`, collects readable eCryptfs lower or upper paths from `/proc/mounts`, then searches each candidate tree for the same inode number.

## State And Persistence Behavior
Reads current mount table and directory trees; does not persist changes.

## Dependencies And Integration Points
Depends on Linux `/proc/mounts`, shell, `ls`, `awk`, and `find`; requires execute/read access to relevant lower or upper trees.

## Risks And Edge Cases
Inode matching can be slow on large trees and can produce ambiguous results across mounts or reused inodes. Parsing `/proc/mounts` by whitespace is fragile for escaped paths.

## Test Signals
Test by creating a file in an eCryptfs mount, locating its lower encrypted path, and verifying the tool maps both directions.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-find -->
