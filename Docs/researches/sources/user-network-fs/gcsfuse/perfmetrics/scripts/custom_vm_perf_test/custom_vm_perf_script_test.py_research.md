## sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script_test.py

Purpose: Unit tests for `custom_vm_perf_script._parse_arguments`.

APIs and control flow: `TestParseArguments` has `test_explicit_values` to assert CLI flags override all defaults and `test_default_values` to assert module constants populate omitted values.

State and persistence: No external state; tests do not mock or execute gcloud VM creation.

Dependencies and risks: Uses Python `unittest`. Coverage is narrow: parsing only, no validation of shell command construction, boot disk size, startup metadata, or error handling.

Test signals: Passing tests prove default and explicit argument mapping only.
