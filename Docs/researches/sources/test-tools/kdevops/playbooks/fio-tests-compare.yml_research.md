# sources/test-tools/kdevops/playbooks/fio-tests-compare.yml

Purpose: compares fio-test results between baseline and dev inventories and generates local comparison graphs.

Important APIs/types/functions: localhost play uses `fail` to require inventory groups, `file` for graph directory creation, `shell` for comparison graph generation, `command` to list results, and `debug` for display.

Control flow: verify both baseline and dev groups exist, prepare output directory, run the graphing/compare command, list generated outputs, and print them.

State/persistence behavior: writes comparison artifacts under local fio result/graph directories.

Dependencies/integration: consumes baseline snapshots from `fio-tests-baseline.yml` and current results from `fio-tests.yml`/`fio-tests-results.yml`.

Risks/test signals: shell-based graph generation depends on path conventions and Python plotting dependencies. Test signals are generated graph files and explicit failure when inventory groups are missing.
