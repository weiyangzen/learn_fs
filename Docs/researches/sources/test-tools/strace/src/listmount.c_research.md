<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/listmount.c -->
# sources/test-tools/strace/src/listmount.c

Purpose: decodes the Linux `listmount` syscall and its versioned `mnt_id_req` input structure.
Important APIs/types/functions: `print_mnt_id_req`, `SYS_FUNC(listmount)`, `struct mnt_id_req`, `MNT_ID_REQ_SIZE_VER*`, `print_array`, `listmount_mnt_id`, and `listmount_flags`.
Control flow: on entry it reads `size`, conditionally fetches known fields, prints future nonzero bytes up to a page; on exit it prints returned mount IDs capped by return value, count, and flags.
State and persistence behavior: stateless; only tracee-memory reads. Dependencies and integration points: mount namespace syscall decoders and xlat tables.
Risks: versioned struct sizes and future fields need careful bounds. Test signals: short, v0, v1, oversized, failed, and successful listmount fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/listmount.c -->
