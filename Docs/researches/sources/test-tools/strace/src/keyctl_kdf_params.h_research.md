# sources/test-tools/strace/src/keyctl_kdf_params.h

Purpose: defines strace's personality-neutral view of keyctl KDF parameters for Diffie-Hellman key computation decoding.

Important APIs/types/functions: `struct strace_keyctl_kdf_params`, `CRYPTO_MAX_ALG_NAME`, `KEYCTL_KDF_MAX_OI_LEN`, `kernel_ulong_t hashname`, `kernel_ulong_t otherinfo`, `otherinfolen`, and `__spare`.

Control flow: header-only constants and structure definition. Pointer fields use `kernel_ulong_t` so the mpers fetch helper can copy tracee pointers into a stable host-side representation.

State and persistence behavior: no state; instances are temporary decoded copies of tracee KDF parameter structs.

Dependencies and integration points: includes `<linux/keyctl.h>` and `kernel_types.h`; used by `keyctl.c` and `fetch_struct_keyctl_kdf_params.c`.

Risks: the structure must match the kernel `keyctl_kdf_params` ABI, including spare fields. Pointer size mismatch would break KDF string/otherinfo decoding.

Test signals: DH compute tests should cover null KDF pointer, valid hash name, zero and nonzero `otherinfolen`, nonzero spare array, and compat pointer widths.
