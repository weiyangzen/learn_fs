# sources/security-integrity/selinux/scripts/oss-fuzz.sh
# sources/security-integrity/selinux/scripts/oss-fuzz.sh

Purpose: builds OSS-Fuzz libFuzzer targets for SELinux components.

Important APIs and control flow: sets sanitizer/compiler flags, DESTDIR, OUT, and fuzzing engine defaults; cleans and installs libsepol/libselinux; compiles and links fuzzers for `secilc`, binary policy, checkpolicy, text fcontext selabel, and compiled fcontext selabel; packages seed corpora and copies a checkpolicy dictionary. It supports OSS-Fuzz environment variables and local mode.

State and persistence: removes/recreates `DESTDIR`, writes fuzzer binaries and seed corpus zips under `OUT`, builds component objects.

Dependencies and integration points: used by ClusterFuzz/OSS-Fuzz; depends on clang/clang++, sanitizer support, make, libsepol/libselinux/checkpolicy sources, zip, PCRE2.

Risks and test signals: script runs with `set -eux` and deletes `DESTDIR`; callers must not point DESTDIR at valuable paths. It intentionally uses unsafe fuzzing build flags. OSS-Fuzz itself is the primary test signal.
