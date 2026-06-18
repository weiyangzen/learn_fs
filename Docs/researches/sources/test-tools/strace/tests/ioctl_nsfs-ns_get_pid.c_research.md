<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid.c -->
# sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid.c

Purpose: tests nsfs PID/TGID translation ioctls for mapping process IDs to or from a pid namespace.

Important APIs/types/functions: Uses `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `syscall(__NR_gettid)`, `/proc/self/ns/pid`, and `linux/nsfs.h` commands `NS_GET_PID_FROM_PIDNS`, `NS_GET_TGID_FROM_PIDNS`, `NS_GET_PID_IN_PIDNS`, and `NS_GET_TGID_IN_PIDNS`.

Control flow: initializes pidns test state, optionally emits pidns translation leader synchronization, first calls all four commands on fd `-1` with synthetic ids, then opens `/proc/self/ns/pid` and repeats with actual TGID/TID values, appending translated-id strings where appropriate.

State and persistence behavior: uses current process pid/tid and namespace fd only; no persistent mutations.

Dependencies/integration points: depends on `/proc`, `linux/nsfs.h`, strace pid namespace helpers, and syscall-number definitions.

Risks and test signals: output depends on pid namespace test harness and whether opening namespace fd succeeds. Passing output confirms command names, argument vs return translation placement, and pidns leader formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid.c -->
