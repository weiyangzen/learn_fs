<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/username.c -->
# sources/user-network-fs/samba/source3/lib/username.c

## Purpose
`username.c` resolves Unix users for Samba by wrapping `getpwnam`, caching passwd records, trying case variants, and honoring `username level` case-combination behavior.

## Important APIs, types, and functions
Public functions are `flush_pwnam_cache`, `get_user_home_dir`, and `Get_Pwnam_alloc`. Internal helpers include `getpwnam_alloc_cached`, `Get_Pwnam_internals`, `uname_string_combinations`, and `uname_string_combinations2`.

## Control flow
`Get_Pwnam_alloc` copies the input into an fstring and calls internals. Resolution tries lowercase first, the original spelling if different, uppercase if different, then combinations with up to `lp_username_level()` uppercase letters. `getpwnam_alloc_cached` checks Samba memcache using a null-terminated string blob key, copies cached passwd data when found, otherwise calls libc `getpwnam`, copies the result into cache, and returns a caller-owned copy. `get_user_home_dir` resolves the user and moves `pw_dir` out of the passwd struct.

## State and persistence behavior
Passwd records are cached in process memory under `GETPWNAM_CACHE`. `flush_pwnam_cache` invalidates that cache. No persistent files are modified.

## Dependencies and integration points
It depends on system passwd APIs, Samba memcache, talloc passwd-copy helpers, loadparm `lp_username_level`, and multibyte-safe case conversion wrappers.

## Risks and edge cases
Case-combination search can become expensive as username level grows. Empty names are rejected. Cache invalidation depends on explicit flush calls when NSS/passwd data changes. Case conversion failure aborts later variants.

## Test signals
Tests should validate cache hit/copy behavior, lower/original/upper lookup order, username-level permutations, empty username rejection, and home directory ownership after moving `pw_dir`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/username.c -->
