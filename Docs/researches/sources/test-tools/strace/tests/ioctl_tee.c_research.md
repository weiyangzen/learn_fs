<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tee.c -->
# sources/test-tools/strace/tests/ioctl_tee.c

Purpose: tests Trusted Execution Environment (`TEE_IOC_*`) ioctl decoding, including version, shared memory allocation/registration, open/invoke/cancel/close session, supplementary receive, and parameter arrays.

Important APIs/types/functions: Uses `linux/tee.h`, `struct tee_ioctl_version_data`, `tee_ioctl_shm_alloc_data`, `tee_ioctl_shm_register_data`, `tee_ioctl_buf_data`, `tee_ioctl_open_session_arg`, `tee_ioctl_invoke_arg`, `tee_ioctl_cancel_arg`, `tee_ioctl_supp_recv_arg`, `tee_ioctl_param`, UUID helpers, `CHK_NULL`, `CHK_BUF`, and generated buffer-with-params structs.

Control flow: calls each TEE ioctl on invalid fd with NULL, bad, and crafted buffers. It fills UUIDs, session ids, command ids, cancellation ids, shared memory ids/sizes/flags, and 14 params spanning none/value/memref temp/registered modes with known and unknown attribute bits. It checks both input-only and before/after forms depending on ioctl direction.

State and persistence behavior: local stack/tail-allocated TEE structs only; invalid fd avoids TEE device state.

Dependencies/integration points: depends on TEE UAPI and strace xlat tables for TEE implementation ids, gen caps, shm flags, and param attrs.

Risks and test signals: TEE struct layouts and attribute flags can change. Passing output confirms nested buffer decoding, UUID formatting, param-array truncation, flag/enumeration expansion, and pointer fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_tee.c -->
