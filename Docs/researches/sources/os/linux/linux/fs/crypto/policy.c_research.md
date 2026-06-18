# File Research: sources/os/linux/linux/fs/crypto/policy.c

## Summary
Implements fscrypt policy validation, policy/context conversion, encryption-policy ioctls, inheritance checks, context creation for new inodes, permitted-context enforcement, and test dummy encryption mount-option parsing/showing.

## Main Responsibilities
- Compare fscrypt policies by version and exact serialized policy size.
- Convert policy versions to master-key specifiers.
- Retrieve filesystem dummy policy hooks.
- Validate v1 and v2 encryption mode combinations.
- Validate flags including padding, DIRECT_KEY, IV_INO_LBLK_64, IV_INO_LBLK_32, and v2 data-unit size.
- Convert policies to on-disk inode contexts and contexts back to policies.
- Set encryption policies on empty directories.
- Return policies via original and extended ioctls.
- Return encryption nonce for testing.
- Enforce that children in encrypted directories have permitted matching policies.
- Provide inheritable policy for new files.
- Build and set contexts for new encrypted inodes.
- Parse, compare, and display `test_dummy_encryption`.

## Key APIs
- `fscrypt_policies_equal()`
- `fscrypt_policy_to_key_spec()`
- `fscrypt_get_dummy_policy()`
- `fscrypt_supported_policy()`
- `fscrypt_policy_from_context()`
- `fscrypt_ioctl_set_policy()`
- `fscrypt_ioctl_get_policy()`
- `fscrypt_ioctl_get_policy_ex()`
- `fscrypt_ioctl_get_nonce()`
- `fscrypt_has_permitted_context()`
- `fscrypt_policy_to_inherit()`
- `fscrypt_context_for_new_inode()`
- `fscrypt_set_context()`
- `fscrypt_parse_test_dummy_encryption()`
- `fscrypt_dummy_policies_equal()`
- `fscrypt_show_test_dummy_encryption()`

## Important Behavior
V1 policies are deprecated and limited to legacy mode combinations. V2 policies allow newer combinations such as AES-256-XTS with AES-256-HCTR2 and SM4-XTS with SM4-CTS, plus v1-compatible combinations.

DIRECT_KEY requires contents and filename modes to match and requires an IV large enough to include the nonce. IV_INO_LBLK policies require AES-256-XTS, stable inode numbers, 32-bit inode numbers, and file data-unit indices that fit in 32 bits. `IV_INO_LBLK_32` is mutually exclusive with sub-block data units for now.

Setting a v2 policy verifies that the current user has added the referenced key, unless privileged override applies elsewhere in key verification. Setting a policy is restricted to owner/capable callers, requires writable mount state, locks the inode, and only succeeds on an empty directory with no existing policy or with the same existing policy.

`fscrypt_has_permitted_context()` allows encrypted children only when their policy matches the encrypted parent, but allows both parent and child with unrecognized policies so deletion remains possible.

## Research Notes
This file defines the compatibility and safety boundary for policy data that reaches disk. It is the main guard against unsupported mode/flag combinations and against inconsistent encrypted directory trees.
