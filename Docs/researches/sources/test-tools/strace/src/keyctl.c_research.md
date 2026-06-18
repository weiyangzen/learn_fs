# sources/test-tools/strace/src/keyctl.c

Purpose: decodes key-management syscalls `add_key`, `request_key`, and the multiplexed `keyctl` command set.

Important APIs/types/functions: `SYS_FUNC(add_key)`, `SYS_FUNC(request_key)`, `SYS_FUNC(keyctl)`, `print_keyring_serial_number`, `keyctl_read_key`, `keyctl_dh_compute`, `keyctl_pkey_query`, `keyctl_pkey_op`, `keyctl_capabilities`, `fetch_keyctl_kdf_params`, `tprint_iov`, and xlats for key specs, permissions, commands, reqkey defaults, pkey ops, move flags, and capabilities.

Control flow: simple add/request syscalls print strings, payloads, lengths, and destination keyrings. `keyctl` prints the operation on entry and dispatches by command. Some commands are entry-only, read-like commands print buffers on exit, DH compute prints parameters on entry and output/KDF parameters on exit, pkey operations save output length for exit decoding, and capabilities are decoded as returned byte arrays.

State and persistence behavior: uses `tcp->aux`/private ulong for pkey output lengths and normal syscall phase state. No durable global state. Tracee memory reads include strings, payload buffers, KDF params, pkey params, and returned capability/output buffers.

Dependencies and integration points: integrates with `fetch_struct_keyctl_kdf_params.c` via `keyctl_kdf_params.h`, generic iovec decoding for `KEYCTL_INSTANTIATE_IOV`, uid/error printers, and generated key xlat tables.

Risks: `keyctl` is multiplexed and new commands must be added carefully to preserve entry/exit returns. Buffer output length is capped by syscall return or user length; KDF `otherinfo` is only valid when `otherinfolen` is nonzero. Pkey encrypt/decrypt/sign differ from verify in `op2` direction.

Test signals: cover add/request, all common keyctl commands, read/describe/security success and error paths, instantiate iov, DH compute with and without KDF otherinfo, pkey query/encrypt/decrypt/sign/verify, move flags, capabilities arrays, and unknown command fallback.
