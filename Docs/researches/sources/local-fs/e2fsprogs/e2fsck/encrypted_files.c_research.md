# File Research: sources/local-fs/e2fsprogs/e2fsck/encrypted_files.c

## Purpose
Tracks encryption policies for encrypted inodes across e2fsck passes so pass 2 can verify children of encrypted directories use the correct policy.

## Data Model
- On-disk fscrypt contexts v1/v2 include policy fields plus nonce.
- In-memory policy strips nonce so files sharing a policy compare equal.
- `encrypted_file_info` contains:
  - run-length encoded inode ranges mapped to policy IDs,
  - red-black tree mapping unique policies to policy IDs,
  - next policy ID counter.
- Special policy IDs represent no xattr, corrupt policy, and unrecognized future policy.

## Main Flow
- `read_encryption_xattr()` reads xattr `"c"` from an inode.
- `fscrypt_context_to_policy()` validates v1/v2 context sizes and extracts policy fields.
- `get_encryption_policy_id()` assigns or reuses policy IDs using an rb-tree.
- `append_ino_and_policy_id()` appends ranges and merges adjacent inode numbers with identical policy IDs.
- `add_encrypted_file()` handles encrypted inodes during pass 1, including missing/corrupt xattr repair decisions.
- `find_encryption_policy()` binary-searches ranges during pass 2.
- Destroy functions release policy tree and ranges.

## Integration
Called from pass 1 for `EXT4_ENCRYPT_FL` inodes and from pass 2 directory checks. State hangs off `ctx->encrypted_files` and is cleaned by `e2fsck_reset_context()`.

## Risks / Notes
The range compression assumes encrypted inodes are processed in strictly increasing inode order and calls `fatal_error()` otherwise.
