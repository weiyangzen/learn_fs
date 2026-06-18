# sources/security-integrity/libcap/tests/libcap_launch_test.c

Purpose: privileged integration test for libcap launcher APIs.

Important APIs/functions: `struct test_case_s` describes launch attributes. `clean_out()` drops all process caps in a callback. Main exercises `cap_new_launcher()`, `cap_func_launcher()`, `cap_launcher_callback()`, `cap_launcher_set_chroot()`, `cap_launcher_setuid()`, `cap_launcher_setgroups()`, `cap_launcher_set_iab()`, `cap_launcher_set_mode()`, `cap_launch()`, and `cap_free()`.

Control flow: iterates table-driven cases, configures launcher attributes, launches, waits, compares wait status against expected result, and finally verifies parent capabilities match the original state.

State and dependencies: spawns child processes, may chroot, changes child uid/gid/IAB/mode, and depends on `../progs/tcapsh-static` plus `noop`.

Risks and test signals: covers launch aborts, callback ordering, IAB propagation, no-priv mode, chrooted static binary execution, and parent-state preservation. A `WITH_PTHREADS` variant links libpsx.
