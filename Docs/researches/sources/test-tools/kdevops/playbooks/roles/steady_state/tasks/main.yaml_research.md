# sources/test-tools/kdevops/playbooks/roles/steady_state/tasks/main.yaml

Purpose: Ansible task list that prepares and runs an SSD steady-state workflow with `fio`, including optional whole-device prefill and IOPS/bandwidth steady-state jobs.

Important APIs/types/functions: uses `include_vars`, role `create_data_partition`, package install, `template` for `ss_iops.ini`/`ss_bw.ini`, `realpath`, `stat`, `/sys/block/*/queue/*`, `blockdev --getsize64`, arithmetic `set_fact` stages, `fio`, local `file`, and `fetch`.

Control flow: imports optional extra vars, creates the data partition and config directory, renders fio configs, resolves and validates `ssd_steady_state_device`, reads device geometry and capacity, computes effective block size and job distribution, validates alignment, runs aligned and remainder prefill jobs, runs the two steady-state jobs, then fetches results to `workflows/steady_state/results/<host>/`.

State/persistence behavior: installs `fio`, creates `steady_state_data`, may overwrite the target block device through prefill writes, produces JSON fio outputs on the target, and copies those artifacts to the controller. Facts such as `effective_blocksize`, `aligned_jobs`, and byte counts are transient Ansible state.

Dependencies/integration: depends on generated kdevops variables such as `kdevops_run_ssd_steady_state`, `ssd_steady_state_*`, `data_device`, and `topdir_path`, plus Linux sysfs/blockdev, root privileges, and the `create_data_partition` role.

Risks/test signals: destructive device writes are gated only by variable correctness and block-device validation. Alignment math and remainder handling are the main correctness risks. Test signals are Ansible syntax success, correct device geometry discovery, fio exit success, and non-empty `ss_iops.json`/`ss_bw.json` fetched to the controller.
