# sources/security-integrity/selinux/.github/workflows/cifuzz.yml

Purpose: GitHub Actions OSS-Fuzz CIFuzz workflow for SELinux fuzz targets.

Important jobs/steps: triggers on push and PR to `master`, only runs for `SELinuxProject/selinux`, and matrixes address, undefined, and memory sanitizers. Uses Google OSS-Fuzz actions to build and run fuzzers for 600 seconds, then uploads crash artifacts on failure after successful build.

Control flow: build fuzzer, run fuzzer, upload artifacts if failing.

State and dependencies: depends on OSS-Fuzz project definition `selinux`, external GitHub actions at `master`, sanitizer support, and generated `out/artifacts`.

Risks and test signals: external action pinning to `master` is mutable. It provides dynamic parser/compiler fuzz coverage, especially for `checkpolicy/fuzz/checkpolicy-fuzzer.c`.
