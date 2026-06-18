<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open03.c

Purpose: CVE-2020-25704 Check for memory leak in PERF_EVENT_IOC_SET_FILTER ioctl command. Fixed in: commit 7bdb157cdebbf95a1cd94ed2e01b338714075d00 Date: Wed Nov 4 08:23:22 2020 +0300 perf/core: Fix a memory leak in perf_event_parse_addr_filter() intel_pt is currently the only event source that supports filters Check how fast we can do the iterations after 5 seconds of runtime. If the rate is too small to complete for current runtime then stop the test.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `tst_timer.h`, `lapi/syscalls.h`, `perf_event_open.h`; exercises `perf_event_open`, `ioctl`; defines `setup`, `check_progress`, `run`, `cleanup`.

Control flow centers on `setup`, `check_progress`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.needs_root` into the LTP runner. Named case hints include `linux-git`, `CVE`.

State and persistence behavior: Runtime state is perf event file descriptors, `perf_event_attr` settings, task/cpu binding, counter enable/disable state, and kernel perf permissions.

Dependencies and integration points: Depends on `perf_event_open.h`, kernel perf support, `/proc/sys/kernel/perf_event_paranoid`, root privileges, CPU affinity helpers, and perf ioctl/read ABI. Direct include dependencies include `config.h`, `tst_test.h`, `tst_timer.h`, `lapi/syscalls.h`, `perf_event_open.h`.

Risks and test signals: Perf tests are sensitive to kernel perf permissions, PMU availability, virtualization, CPU scheduling, and multiplexing precision. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open03.c -->
