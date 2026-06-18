# File Research: sources/os/bsd/freebsd-src/sbin/md5/tests/md5_test.sh

## Summary
ATF shell test generator for FreeBSD digest utilities. It validates BSD-style digest tools, GNU `*sum` compatibility modes, Perl-compatible `shasum` modes where supported, self-tests, and checksum verification behavior across many algorithms.

## Main Elements
- Defines 8 canonical input vectors and expected outputs for `md5`, SHA variants, RIPEMD-160, and Skein variants.
- Generates ATF test cases with shell `eval` loops for each algorithm and vector.
- Tests BSD output modes: stdin, file, `-`, reverse `-r`, quiet `-q`, passthrough `-p`, and string `-s`.
- Tests GNU output modes: text, binary `-b`, `--tag`, NUL-terminated `-z`, and check mode `-c`.
- Tests Perl `shasum` compatibility for SHA algorithms, including binary and universal input modes.
- Adds targeted tests for GNU binary output, missing-file handling in check mode, `--ignore-missing`, and input-mode parsing.

## Dependencies And Integration
Uses FreeBSD ATF shell APIs: `atf_test_case`, `atf_set`, `atf_check`, and `atf_add_test_case`. Requires the relevant digest utility names (`md5`, `sha256`, `sha256sum`, `shasum`, etc.) per test case.

## Research Notes
The test file is mostly declarative vectors plus dynamic ATF test construction. Its coverage is broad because each vector is checked through multiple command-line compatibility surfaces, not just raw digest calculation.
