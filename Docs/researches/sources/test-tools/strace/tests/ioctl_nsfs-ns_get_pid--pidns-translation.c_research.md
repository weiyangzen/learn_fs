<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid--pidns-translation.c

Purpose: pid-namespace translation variant for `NS_GET_{PID,TGID}_{FROM,IN}_PIDNS` decoding. It defines `PIDNS_TRANSLATION` before including `ioctl_nsfs-ns_get_pid.c`.

Important APIs/types/functions: Inherits pidns helper APIs (`PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`), `NS_GET_PID_FROM_PIDNS`, `NS_GET_TGID_FROM_PIDNS`, `NS_GET_PID_IN_PIDNS`, and `NS_GET_TGID_IN_PIDNS`.

Control flow: the included test prints a leader marker before ioctl lines and emits an initial `NS_GET_USERNS` synchronization probe, then runs the base PIDNS get/in/from ioctl cases.

State and persistence behavior: no persistent state; pid namespace mappings are runtime-only observations of the current process and namespace fd.

Dependencies/integration points: integrates strace pid namespace translation output with nsfs ioctl decoding and `/proc/self/ns/pid`.

Risks and test signals: sensitive to pid namespace availability and expected translated PID suffixes. Passing output confirms translated argument and return PID rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_nsfs-ns_get_pid--pidns-translation.c -->
