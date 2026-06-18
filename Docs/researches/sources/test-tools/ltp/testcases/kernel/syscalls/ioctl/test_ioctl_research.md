# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/test_ioctl

Purpose: legacy shell harness for running `ioctl02` against usable tty devices discovered under `/dev/tty*`.

Important APIs/types/functions: shell functions `has_tty`, `stty -F`, `tst_resm`, `ioctl02 -d`, and `tst_exit`.

Control flow: exports LTP legacy counters, iterates numeric tty device names, skips unusable ttys, runs `ioctl02` with the device path, and reports TPASS/TFAIL from the child program exit status.

State and persistence behavior: no durable state beyond invoking `ioctl02`; it probes terminal devices and relies on the child test to restore tty attributes.

Dependencies and integration points: installed by the ioctl Makefile as `test_ioctl`; depends on the legacy LTP shell API and on `ioctl02` being built and reachable in PATH.

Risks: device enumeration is host-dependent, and the `has_tty` helper treats `stty` failures as skip candidates, so coverage varies by console configuration.

Test signals: emits TPASS/TFAIL per tty based on `ioctl02`'s exit code and exits through the LTP shell harness.
