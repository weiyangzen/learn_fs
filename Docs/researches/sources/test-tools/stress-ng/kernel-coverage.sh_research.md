# sources/test-tools/stress-ng/kernel-coverage.sh

## Purpose
`kernel-coverage.sh` is a privileged, destructive-by-design kernel coverage harness that runs stress-ng workloads across schedulers, filesystems, I/O paths, memory controls, and stressor option combinations, then collects gcov/lcov reports.

## Important APIs, Types, And Functions
It defines `get_stress_ng_pids`, `kill_stress_ng`, `mount_filesystem`, `umount_filesystem`, `clear_journal`, and `do_stress`. It configures swap, perf permissions, core pattern, OOM score adjustment, lcov counters, branch tracing snapshots, many loop-mounted filesystems, scheduler and ionice sweeps, every discovered stressor, and a long list of stressor-specific option runs. It ends by collecting `kernel.info`, generating HTML, and converting HTML to text.

## Control Flow
The script validates `STRESS_NG`, derives stressor names from `--stressors` with `smi` removed, adjusts kernel tunables, creates a 2 GiB swap file, zeroes coverage counters, then runs staged workloads. Filesystem stages create images or special mounts, run I/O/filesystem stressors with several options and I/O schedulers, then unmount and clean. Later stages sweep schedulers, ionice classes, all stressors, and targeted option permutations. Cleanup restores swap, core pattern, perf paranoid, and generates coverage reports.

## State And Persistence
It writes `/tmp/swap.img`, `/tmp/fs.img`, `/tmp/sng-mnt-*` mount points, `/tmp/lower`, `/tmp/upper`, `/tmp/work` for overlay, local logs, `branch_all.start`, `branch_all.finish`, `kernel.info`, and `html/`. It writes kernel controls under `/proc/sys`, may load/unload modules such as nandsim/ubi/ubifs, changes I/O schedulers, mounts filesystems, vacuums journal logs, and runs stress-ng as root.

## Dependencies And Integration Points
It depends on bash, sudo, stress-ng, lcov/genhtml/html2text, mkfs tools for many filesystems, loop mounts, debugfs/gcov kernel configuration, `/sys/kernel/debug/tracing`, and numerous kernel features. It integrates directly with almost every stressor, `core-vmstat` status/iostat/thermal/RAPL paths, syslog/klog/perf reporting, and the stressor registry.

## Risks
This script is not a normal test; it mutates system-wide settings and can consume substantial CPU, memory, disk, and time. It uses unquoted variables in many places, assumes Linux root privileges, may leave mounts/images/modules if interrupted, and deliberately runs pathological stressors. Filesystem and kernel-feature assumptions can fail on minimal systems.

## Test Signals
Primary success signals are completed lcov/genhtml output and absence of unrecovered mounts or stuck stress-ng processes. Intermediate logs show each `STARTED`/`FINISHED` run, filesystem mount status, scheduler sweeps, and stressor return codes. Coverage growth in `kernel.info` is the intended output.
