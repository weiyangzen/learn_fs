<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/steady_state/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/steady_state/defaults/main.yml

Purpose: defines SSD steady-state prefill and fio run criteria: data path, device, block size, iodepth, jobs, runtime, IOPS/BW mean and slope thresholds, and prefill options.

Important APIs/types/functions: variables/facts `steady_state_data`, `ssd_steady_state_device`, `ssd_steady_state_prefill_blocksize`, `ssd_steady_state_iodepth`, `ssd_steady_state_numjobs`, `ssd_steady_state_prefill_loop`, `ssd_steady_state_runtime`, `ssd_steady_state_iops_mean_limit`, `ssd_steady_state_iops_mean_dur`, `ssd_steady_state_iops_slope`.

Control flow: Defaults are consumed by steady-state workflow tasks outside this subset to build fio commands and acceptance gates.

State and persistence behavior: No direct state; values shape fio workload and result thresholds.

Dependencies and integration points: Integrated with storage performance workflows that need preconditioning before measurement.

Risks: Long default runtime and repeated prefill can consume device endurance/time. Device default `/dev/null` is safe but not useful unless overridden.

Test signals: Signals are generated fio command arguments matching defaults and threshold evaluation over collected metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/steady_state/defaults/main.yml -->
