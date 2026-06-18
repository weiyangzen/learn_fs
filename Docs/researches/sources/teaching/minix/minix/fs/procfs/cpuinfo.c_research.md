# File Research: sources/teaching/minix/minix/fs/procfs/cpuinfo.c

`cpuinfo.c` generates `/proc/cpuinfo`. On i386, it defines a CPU feature-bit name table and `print_x86_cpu_flags`, which emits supported feature names for two 32-bit flag words.

`print_cpu` emits a processor number and, for i386, vendor, model-family fields, frequency, and feature flags based on `struct cpu_info`. Vendor mapping currently names Intel and AMD explicitly and falls back to `unknown`.

`root_cpuinfo` fetches machine topology with `sys_getmachine` and CPU details with `sys_getcpuinfo`, logging failures to the console. It iterates over `machine.processors_count` and appends each CPU's information through the ProcFS buffer API.
