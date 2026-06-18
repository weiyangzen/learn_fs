# sources/security-integrity/selinux/python/semanage/test-semanage.py

## Purpose
This file is an integration-style unittest harness for the installed `semanage` command. It verifies that selected semanage subcommands can list, extract, export/import, and perform several add/modify/delete cycles against a live enforcing SELinux system.

## Important APIs, types, and functions
- `object_list` enumerates tested subcommands: login, user, port, module, interface, node, fcontext, boolean, permissive, and dontaudit.
- `SemanageTests` contains helper assertions and test methods.
- `test_extract()`, `test_input_output()`, `test_list()`, `test_list_c()`, `test_fcontext()`, `test_fcontext_e()`, `test_port()`, `test_login()`, `test_user()`, and `test_boolean()` execute command subprocesses.
- `semanage_suite()`, `semanage_custom_suite()`, and `semanage_run_test()` build and run unittest suites.
- `CheckTest` validates names passed to `-t/--test`.
- `gen_semanage_test_args()` installs the script's own CLI.

## Control flow
When run as a script, it imports `selinux`, builds `semanage_test_list` from methods beginning with `test_`, and only enables argument parsing when SELinux is enabled and enforcing. The user can list tests, run all tests, or run selected test names. Each test uses `subprocess.Popen` to invoke real system commands, waits with `communicate()`, and asserts status with helper methods.

## State and persistence behavior
The tests deliberately mutate the live system policy store and user database. They create and delete file context mappings for `/ha-web`, fcontext equivalence mappings for `/myhome` and `/myhome1`, TCP port 55 mappings, a Linux user `testlogin`, an SELinux user `testuser_u`, a login mapping, and `httpd_anon_write` boolean state. Export writes `/tmp/out` and import replays it. Cleanup commands are issued before many tests but are best-effort and sometimes do not assert cleanup success.

## Dependencies and integration points
The harness depends on Python `unittest`, `argparse`, `sys`, and `subprocess`, plus installed host commands `semanage`, `useradd`, `userdel`, and a Python `selinux` module. It requires SELinux enforcing mode, policy names such as `targeted`, roles/types such as `staff_r`, `staff_u`, `ssh_port_t`, `http_port_t`, `httpd_sys_content_t`, and boolean `httpd_anon_write`.

## Risks and edge cases
- These are destructive integration tests against the current machine, not isolated unit tests.
- Some subprocesses capture only stdout or only stderr, and many ignore output from cleanup operations.
- `assertSuccess()` and `assertFailure()` use `assertTrue` with static strings, so diagnostics can omit command context.
- `test_fcontext_e()` prints "Verify semanage fcontext -m -e" but runs `-a -e` for `/myhome1`; modify-equivalence behavior is not actually tested.
- `test_login()` does not assert success for the `semanage login -d` cleanup in the main test path.
- `assertDenied()` and `assertNotFound()` are unused.
- The test set omits ibpkey, ibendport, interface mutation, node mutation, module add/remove/enable/disable, permissive mutation, dontaudit, failure modes, and parser conflict validation.

## Test signals
Passing this suite indicates basic installed-command functionality on a permissive test host with the expected policy vocabulary. It is not suitable for normal unprivileged CI unless run inside a disposable SELinux-enabled environment.
