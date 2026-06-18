# sources/test-tools/kdevops/playbooks/fio-tests.yml

Purpose: primary fio performance test runner for baseline/dev hosts.

Important APIs/types/functions: targets `baseline` and `dev`, sets `ansible_ssh_pipelining: true`, runs role `create_data_partition` with tag `data_partition`, then role `fio-tests`.

Control flow: prepare data storage first, then execute fio workload orchestration.

State/persistence behavior: creates or validates data partitions and writes fio result JSONs/logs under workflow result directories.

Dependencies/integration: integrates storage provisioning, fio-test role configuration, result collection, graphing, baseline, and comparison playbooks.

Risks/test signals: data partition setup can be destructive depending on role variables. Test signals are fio JSON result files, expected target devices, and successful repeated idempotent setup.
