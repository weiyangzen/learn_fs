# sources/test-tools/syzkaller/executor/test.h

Purpose: Built-in executor self-tests selected by `syz-executor test [name]`.

Important APIs and control flow: includes Linux KVM tests for supported architectures. `test_copyin` validates bitfield/endian store macros. `test_csum_inet` and `test_csum_inet_acc` validate Internet checksum fixed vectors and incremental update equivalence. `test_cover_filter` validates parent/child shared filter membership and false-positive granularity. `test_glob` builds a local tree and validates file/symlink behavior. `test_get_last_opt` checks command-line option parsing. `tests[]` registers test names and `run_tests` executes all or one named test with RUN/OK/FAIL/SKIP output.

State and dependencies: tests create files in cwd and use global executor helpers/macros. Some tests are arch/OS gated.

Integration points: invoked by `main` before normal `exec` mode. The tests cover helpers used by csource, runner handshakes, coverage filtering, and KVM setup.

Risks and tests: `test_glob` intentionally skips on 32-bit ARM under QEMU due to known `readdir` overflow. KVM tests require `/dev/kvm` and permissions. The file is both implementation and test signal for many helper contracts.
