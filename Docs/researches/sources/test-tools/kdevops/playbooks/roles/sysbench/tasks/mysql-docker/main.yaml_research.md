# sources/test-tools/kdevops/playbooks/roles/sysbench/tasks/mysql-docker/main.yaml

Purpose: end-to-end MySQL-in-Docker sysbench workflow that formats a target device, starts MySQL and sysbench containers, populates and runs OLTP workload, gathers telemetry, and plots results.

Important APIs/types/functions: uses `set_fact` for A/B device and filesystem selection, Docker modules `community.docker.docker_container` and `docker_container_exec`, role `create_partition`, templates for MySQL client/server config, git clone of telemetry plugin, async sysbench execution, `async_status`, `fetch`, `journalctl`, debugfs extfrag files, and local Python plotting scripts.

Control flow: resolves per-host device, creates telemetry/root directories, derives filesystem command/page size/sector size, removes stale containers, unmounts and wipes target device, creates filesystem, toggles InnoDB doublewrite for baseline/dev modes, writes MySQL config, starts MySQL, verifies socket/client access, creates database user/grants, installs telemetry Python dependencies inside the container, starts a reusable sysbench container, populates the database, runs sysbench asynchronously while telemetry collection runs, waits for completion, collects logs and host kernel/memory signals, optionally cleans results, and generates per-node/A-vs-B/variance plots.

State/persistence behavior: destructive on `sysbench_device`; creates/mounts `sysbench_mnt`, Docker containers, `/data` MySQL/config/telemetry paths, controller result directories, and plot artifacts. It also writes config and metadata such as kernel version, doublewrite setting, and page size.

Dependencies/integration: depends on Docker, MySQL image/client, `severalnines/sysbench`, kdevops filesystem command variables, `create_partition`, `sysbench_db_*` credentials, and Python plotting scripts under `playbooks/python/workflows/sysbench`.

Risks/test signals: primary risks are destructive wipefs on the wrong device, fragile container readiness checks, credential exposure in task output, telemetry plugin/network dependency, and async polling duration. Test signals include successful MySQL socket checks, sysbench populate/run logs, `sysbench_tps.txt`, copied telemetry, dmesg/extfrag captures, and generated plots.
