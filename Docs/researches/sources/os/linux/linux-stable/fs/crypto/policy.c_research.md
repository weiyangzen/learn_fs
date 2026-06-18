# File Research: sources/os/linux/linux-stable/fs/crypto/policy.c

## Summary
Implements fscrypt policy validation, conversion between policy and on-disk context formats, policy ioctls, permitted-context checks, inheritance, context creation for new inodes, and test dummy encryption option parsing/display.

## Main Responsibilities
- Compare fscrypt policies by version-specific size.
- Convert policies to master-key specifiers.
- Validate v1 and v2 encryption mode combinations and flags.
- Enforce DIRECT_KEY, IV_INO_LBLK, casefold, stable-inode, 32-bit-inode, max-file-size, and sub-block data-unit constraints.
- Create on-disk fscrypt contexts from policies and nonces.
- Reconstruct policies from on-disk contexts.
- Get, set, and export encryption policies through ioctls.
- Export encryption nonces for testing.
- Enforce that encrypted directories contain only children with permitted matching policies.
- Determine the policy new children inherit from encrypted directories or dummy-encryption mounts.
- Write fscrypt contexts for newly prepared inodes.
- Parse, compare, and show `test_dummy_encryption` mount policies.

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
V1 policies are intentionally restricted to legacy mode combinations and only support padding plus DIRECT_KEY flags. They are rejected for casefolded directories because v1 has no way to derive the secret dirhash key.

V2 policies add AES-HCTR2 filename mode pairing, SM4 pairings, IV_INO_LBLK flags, and configurable data-unit sizes. Mutually exclusive flags are rejected. IV_INO_LBLK policies require AES-256-XTS contents mode, filesystem-stable inode numbers, 32-bit inode numbers, and file data-unit indices that fit in 32 bits.

Setting a v2 policy verifies that the current user has added the referenced master key, unless overridden by `CAP_FOWNER`. Setting a v1 policy emits a warning recommending v2. Setting a policy is allowed only on an owned/capable empty directory that does not already have a different policy.

`fscrypt_has_permitted_context()` allows deletion of children when both parent and child have unrecognized policies, but otherwise requires matching policies under encrypted parents and forbids unencrypted children in encrypted directories.

## Research Notes
This file is the policy gatekeeper. It separates syntactic context conversion from semantic support checks, and it enforces the filesystem properties required for IV schemes that depend on inode numbers or data-unit geometry.
