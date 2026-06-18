# sources/security-integrity/libcap/progs/capsh.c

Purpose: multifunction capability shell/diagnostic launcher used by users and by libcap's privileged test suite.

Important APIs/functions: helpers parse numbers, print process/IAB/securebits state, drop bounding bits, edit ambient bits, locate `capsh` in `PATH`, describe capabilities from `capshdoc.c`, and launch commands via `cap_launch()`. Main option handling covers `--caps`, `--inh`, `--iab`, `--drop`, `--addamb`, `--delamb`, `--mode`, `--secbits`, `--keep`, uid/gid/group changes, chroot, `--no-new-privs`, assertions, explain/suggest, shell exec, and cap-launch paths.

Control flow: options are processed sequentially, so earlier capability or identity changes affect later operations. `--`, `==`, `-+`, and `=+` replace the process with a shell or re-execed `capsh`, optionally through `cap_launch()`.

State and dependencies: mutates process capabilities, IAB, ambient set, securebits, uid/gid/groups, environment, chroot, and child processes. Depends on libcap, prctl, NSS, wait/fork/exec, and generated doc arrays.

Risks and test signals: option order is security relevant. Non-strict mode temporarily raises `CAP_SETPCAP` or `CAP_SYS_CHROOT`; failures restore only by process exit. `quicktest.sh` heavily exercises mode transitions, bounding/ambient semantics, chroot, namespace file caps, and assertion options.
