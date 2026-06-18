<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open02.c

Purpose: Here's a little test program that checks whether software counters (specifically, the task clock counter) work correctly when they're in a group with hardware counters. What it does is to create several groups, each with one hardware counter, counting instructions, plus a task clock counter. It needs to know an upper bound N on the number of hardware counters you have (N defaults to 8), and it creates N+4 groups to force them to be multiplexed. It also creates an overall task clock counter. Then it spins for a while, and then stops all the counters and reads them. It takes the total of the task clock counters in

Important APIs/types/functions: includes `errno.h`, `sched.h`, `signal.h`, `stddef.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`; exercises `perf_event_open`, `prctl`, `read`, `ioctl`, `sched_setaffinity`; defines `all_counters_set`, `alarm_handler`, `bench_work`, `do_work`, `count_hardware_counters`, `bind_to_current_cpu`, `setup`, `cleanup`, `verify`; uses flags/constants `PR_TASK_PERF_EVENTS_DISABLE`, `PR_TASK_PERF_EVENTS_ENABLE`.

Control flow centers on `all_counters_set`, `alarm_handler`, `bench_work`, `do_work`, `count_hardware_counters`, `bind_to_current_cpu`, `setup`, `cleanup`, `verify`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.needs_root`, `.timeout` into the LTP runner.

State and persistence behavior: Runtime state is perf event file descriptors, `perf_event_attr` settings, task/cpu binding, counter enable/disable state, and kernel perf permissions.

Dependencies and integration points: Depends on `perf_event_open.h`, kernel perf support, `/proc/sys/kernel/perf_event_paranoid`, root privileges, CPU affinity helpers, and perf ioctl/read ABI. Direct include dependencies include `errno.h`, `sched.h`, `signal.h`, `stddef.h`, `stdio.h`, `stdlib.h`.

Risks and test signals: Perf tests are sensitive to kernel perf permissions, PMU availability, virtualization, CPU scheduling, and multiplexing precision. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open02.c -->
