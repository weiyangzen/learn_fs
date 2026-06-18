# sources/test-tools/strace/src/seccomp.c

Purpose: decodes the `seccomp` syscall operations and operation-specific argument payloads.

Important APIs/types/functions: `SYS_FUNC(seccomp)`, `decode_seccomp_fprog`, `seccomp_ops`, `seccomp_filter_flags`, `seccomp_ret_action`, and `struct seccomp_notif_sizes`.

Control flow: prints operation on entry, then switches by op. `GET_ACTION_AVAIL` prints raw flags and dereferences an action value. `GET_NOTIF_SIZES` prints flags on entry and decodes returned sizes on exit. `SET_MODE_FILTER` prints filter flags and BPF program. Strict mode and unknown operations print raw flags and address.

State and persistence behavior: no persistent state; reads pointed arguments only when meaningful for the selected operation and syscall phase.

Dependencies and integration points: uses Linux seccomp UAPI, BPF filter decoder, and xlat tables. Pairs with `seccomp_ioctl.c` for user-notification file-descriptor ioctls.

Risks: seccomp operation semantics differ by direction; new operations may need phase-sensitive decoding. `GET_NOTIF_SIZES` carries future-size hints that need ABI-aware tests.

Test signals: cover strict/filter modes, action availability, notification sizes success/failure, unknown ops, invalid pointers, and flag name rendering.
