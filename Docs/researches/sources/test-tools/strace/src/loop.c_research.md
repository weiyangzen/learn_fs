<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/loop.c -->
# sources/test-tools/strace/src/loop.c

Purpose: decodes loop-device ioctls and loop status/configuration structures.
Important APIs/types/functions: `loop_ioctl`, `decode_loop_info`, `decode_loop_info64`, `decode_loop_config`, mpers `struct_loop_info`, `loop_flags_options`, and `loop_crypt_type_options`.
Control flow: switch by ioctl code; GET operations often wait for exit, SET/CONFIGURE decode entry arguments, fd/numeric/no-arg commands are printed directly, and unknown commands fall back.
State and persistence behavior: stateless tracee-memory reads, with abbreviated output hiding less important fields. Dependencies and integration points: central ioctl dispatcher and mpers type generation.
Risks: old/new loop structs and encryption key sizes are ABI-sensitive. Test signals: LOOP_GET/SET_STATUS, STATUS64, CONFIGURE, fd-changing, and no-argument ioctl fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/loop.c -->
