<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_mq_attr.c -->
# sources/test-tools/strace/src/print_mq_attr.c

Purpose: mpers-aware printer for POSIX message queue attributes.

Important APIs/types/functions: `printmqattr`, `mq_attr_t`, and `mq_attr_flags`.

Control flow: fetches `struct mq_attr`; prints `mq_flags` symbolically when requested or hex otherwise, then prints max messages, message size, and current message count.

State and persistence behavior: no state.

Dependencies and integration points: used by mqueue syscall decoders; depends on mpers, kernel mqueue headers, and open-flag style xlat tables.

Risks: layout is personality-sensitive. Callers must choose `decode_flags` according to syscall context.

Test signals: `mq_getsetattr`, `mq_open` attribute printing, native/compat layouts, flags decoded/raw modes, and invalid pointer fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_mq_attr.c -->
