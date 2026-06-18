## sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script.py

Purpose: Creates a configurable GCE VM for custom performance tests with a startup script.

APIs and control flow: `_parse_arguments(argv)` defines defaults for VM name, machine type, image family/project, zone, and startup script. In `__main__`, it builds a `gcloud compute instances create` command with a 100GiB boot disk and metadata startup script, then invokes it via `subprocess.check_output(..., shell=True)`.

State and persistence: Creates a real VM and attaches startup-script metadata. No cleanup is implemented.

Dependencies and risks: Requires gcloud auth/quota. `_parse_arguments` ignores its argument parameter except for `argv[1:]` after replacing `argv = sys.argv` in the caller context; tests call it directly with a script-name-prefixed list. Shell string construction exposes command-injection risk if untrusted args are passed.

Test signals: Unit tests cover explicit and default argument parsing, not VM creation.
