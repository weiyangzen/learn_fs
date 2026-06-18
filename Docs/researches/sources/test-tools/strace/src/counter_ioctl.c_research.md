<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/counter_ioctl.c -->
## sources/test-tools/strace/src/counter_ioctl.c

Purpose: Decodes Linux Counter subsystem ioctl arguments.

Important APIs and types: `print_struct_counter_component`, `print_struct_counter_watch`, and exported `counter_ioctl`.

Control flow: For `COUNTER_ADD_WATCH_IOCTL`, prints `argp`, fetches `struct counter_watch`, and prints nested component type/scope/parent/id plus event and channel. `COUNTER_ENABLE_EVENTS_IOCTL` and `COUNTER_DISABLE_EVENTS_IOCTL` take no decoded argument but return `RVAL_IOCTL_DECODED`. Unknown counter ioctls return `RVAL_DECODED`.

State and persistence: No state.

Dependencies and integration: Depends on `defs.h`, `<linux/ioctl.h>`, `<linux/counter.h>`, and counter xlat tables. Integrated into the generic ioctl decoder.

Risks: Uses `CHECK_IOCTL_SIZE` and `CHECK_TYPE_SIZE` for expected layout; kernel UAPI changes require updates. Nested component decoding depends on host header availability.

Test signals: Tests should cover add-watch with each xlat field, enable/disable events, unreadable pointers, and unknown ioctl fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/counter_ioctl.c -->
