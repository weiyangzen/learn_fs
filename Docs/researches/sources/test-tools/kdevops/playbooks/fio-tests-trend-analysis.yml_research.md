# sources/test-tools/kdevops/playbooks/fio-tests-trend-analysis.yml

Purpose: generates trend analysis artifacts for fio-test results on baseline/dev hosts.

Important APIs/types/functions: targets `baseline` and `dev`, includes the `create_data_partition` role under tags `oscheck` and `data_partition`, then uses shell to run trend analysis and command/debug to list generated files.

Control flow: ensure data partition prerequisites, run the trend analysis command, list outputs, and display paths.

State/persistence behavior: writes analysis files into fio workflow result directories and may ensure `/data` or equivalent storage exists.

Dependencies/integration: depends on fio-test result layout, trend analysis script availability, and create-data-partition role variables.

Risks/test signals: shell command path assumptions are the main fragility. Test signals are generated trend artifacts and successful listing output.
