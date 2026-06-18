# sources/security-integrity/libcap/progs/quicktest.sh

Purpose: privileged integration test script for `capsh`, `setcap`, `getcap`, `getpcaps`, namespace file capabilities, ambient capabilities, securebits, chroot, and kernel bug probes.

Important functions: `try_capsh`, `fail_capsh`, and `pass_capsh` standardize expected pass/fail assertions. The script builds local test binaries, manipulates file capabilities, creates symlinks and shell scripts, and runs `uns_test`.

Control flow: starts with basic `capsh` state checks and re-exec path checks, then tests libcap modes, setuid/keepcaps flows, securebits, bounding set behavior, inheritable and ambient capabilities, chroot, namespace rootid file caps, optional Go binary checks, and a user namespace exploit regression.

State and dependencies: requires root-like privilege, sudo, working build products, filesystem xattrs, user `nobody`, and kernel support for tested features.

Risks and test signals: it mutates local files and capabilities, so it must run in the build directory. Fail/pass inversion is deliberate for negative tests. It is the highest-level test signal for `capsh` behavior.
