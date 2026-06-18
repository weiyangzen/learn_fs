<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.h -->
# sources/security-integrity/keyutils/keyutils.h

## Purpose

`keyutils.h` is the public C API and ABI definition for libkeyutils. It defines key serial and permission types, special keyring IDs, keyctl command numbers, request-key defaults, DH/KDF/pkey structures, capability flags, move flags, syscall wrappers, typed keyctl wrappers, and utility helpers.

## Important APIs, Types, and Functions

Core types are `key_serial_t` and `key_perm_t`. Constants include `KEY_SPEC_*`, `KEY_REQKEY_DEFL_*`, permission masks for possessor/user/group/other classes, `KEYCTL_*` command numbers 0..32, `KEYCTL_SUPPORTS_*`, `KEYCTL_MOVE_EXCL`, and `KEYCTL_CAPS*`. Structures include `keyctl_dh_params`, `keyctl_kdf_params`, `keyctl_pkey_query`, and `keyctl_pkey_params`. Function prototypes expose `add_key()`, `request_key()`, variadic `keyctl()`, all typed wrappers, allocation helpers, recursive scanning, and `find_key_by_type_and_desc()`.

## Control Flow

This header has no runtime control flow. It establishes the binary/source contract consumed by `keyutils.c`, `keyctl.c`, request-key, and outside callers.

## State and Persistence Behavior

No state is stored here. The declared APIs operate on kernel-retained key state and may allocate caller-owned buffers when using `_alloc` helpers.

## Dependencies and Integration Points

The header is C/C++ compatible via `extern "C"`. It includes `sys/types.h` and `stdint.h`, forward-declares `struct iovec`, and must match kernel UAPI command numbers and structure layouts.

## Risks and Edge Cases

ABI drift is the primary risk: command numbers, structure padding, and integer widths must remain compatible with kernel expectations and existing applications. The variadic `keyctl()` prototype exposes weak type checking, so typed wrappers are safer for callers. Public constants require careful extension to avoid reusing bits or command numbers.

## Test Signals

Build tests should compile C and C++ users, verify structure sizes/layouts where ABI matters, and exercise each public wrapper against a kernel with matching keyring support.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.h -->
