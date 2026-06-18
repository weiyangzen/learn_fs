# sources/security-integrity/libcap/tests/Makefile

Purpose: builds and runs libcap/libpsx C test programs.

Important targets: unprivileged `run_psx_test`, `run_libcap_psx_test`; privileged `run_uns_test`, `run_libcap_launch_test`, `run_libcap_psx_launch_test`, `run_exploit_test`; dynamic shared bug test `run_b219174`; build targets for `noop`, `exploit`, `noexploit`, `weaver.so`, and `b219174`.

Control flow: test target runs PSX tests when `PTHREADS=yes`; `sudotest` adds privileged tests under sudo. Linkage switches between static and dynamic libcap/libpsx, with rpath for dynamic tests.

State and dependencies: depends on `../libcap` artifacts, `../progs/tcapsh-static`, pthreads, sudo, dlopen for b219174, and build variables.

Risks and test signals: library order for `noexploit` is security relevant. The suite distinguishes vulnerable libcap-only threading from protected libpsx-linked behavior.
