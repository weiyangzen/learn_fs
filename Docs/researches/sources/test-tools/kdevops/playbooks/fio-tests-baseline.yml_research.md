# sources/test-tools/kdevops/playbooks/fio-tests-baseline.yml

Purpose: saves current fio-test result configuration as a baseline for later comparison.

Important APIs/types/functions: targets `baseline` and `dev`, disables become, enables SSH pipelining, uses `file`, `copy` with `with_fileglob`, and `shell` to create a timestamp.

Control flow: create baseline directory structure, copy current result/configuration files into it, then write a timestamp marker.

State/persistence behavior: persists baseline result snapshots under the fio workflow area so comparison playbooks can detect regressions.

Dependencies/integration: paired with `fio-tests-compare.yml`, `fio-tests-results.yml`, and the `fio-tests` role output layout.

Risks/test signals: fileglob copy behavior can silently copy nothing if result paths differ. Test signals are non-empty baseline directories, timestamp file, and compare playbook finding both baseline and dev inputs.
