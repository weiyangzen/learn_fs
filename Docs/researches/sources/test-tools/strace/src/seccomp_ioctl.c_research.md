# sources/test-tools/strace/src/seccomp_ioctl.c

Purpose: decodes ioctls on seccomp user-notification file descriptors.

Important APIs/types/functions: `seccomp_ioctl`, `print_struct_seccomp_data`, `print_struct_seccomp_notif`, `print_struct_seccomp_notif_resp`, `print_struct_seccomp_notif_addfd`, `SECCOMP_IOCTL_NOTIF_ID_VALID_WRONG_DIR`, and notification/addfd/response xlat tables.

Control flow: `NOTIF_RECV` prints `argp` on entry, suppresses all-zero input structs, and on exit prints notification id, pid, flags, syscall data, arch, IP, and args. `NOTIF_SEND` prints response id/value/error/flags. ID-valid ioctls print a 64-bit id. `ADDFD` decodes source fd, target fd, addfd flags, and open flags. `SET_FLAGS` decodes flags passed directly in the ioctl argument.

State and persistence behavior: no private persistent state; behavior is phase-sensitive for `NOTIF_RECV` because the kernel fills the struct on exit.

Dependencies and integration points: uses seccomp UAPI, audit arch xlat, syscall-name printer, open mode flags, and ioctl size/type checks to detect ABI drift.

Risks: ioctl numbers encode struct sizes, so UAPI changes can break decoding; the file explicitly guards expected sizes. `NOTIF_ID_VALID_WRONG_DIR` compatibility exists for a direction mismatch and should not be removed without test updates.

Test signals: seccomp notification receive with zero/nonzero entry buffers, successful response, negative errno response, addfd flags, id-valid variants, set-flags, and ABI size assertions during build.
