# sources/test-tools/kdevops/playbooks/build_linux_results.yml

Purpose: collects build-linux result artifacts from target hosts and generates a combined local report.

Important APIs/types/functions: targets `all`, sets `build_linux_results_dir` defaulting to `workflows/build-linux/results`, uses `file`, `stat`, `find`, `fetch`, `copy`, `command`, and `debug`. Local tasks are delegated to `localhost` and run once.

Control flow: create local result directory, check each target for results, list and fetch files, copy a combine script locally, run it when files exist, remove the temporary script, and display report lines.

State/persistence behavior: writes fetched result files and a combined report into the local workflow results directory. It also creates and then removes a temporary script.

Dependencies/integration: consumes artifacts created by the `build_linux` role and feeds local reporting. Uses Ansible delegation and registered `result_files` state.

Risks/test signals: conditions reference `result_files.matched` in run-once local tasks even though `result_files` is registered per host, so multi-host aggregation can be fragile. Test signals are fetched files, successful combine command, and visible combined report output.
