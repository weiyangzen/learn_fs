# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test_probe.in

## Purpose
`test_probe.in` is the shell regression driver for the blkid probe image corpus.

## Important APIs, Types, and Functions
It is a configured shell script using `SRCDIR`, `tst_probe`, `bunzip2`, `dd`, `mkswap`, `cmp`, `diff`, and filesystem result files under `tests/`.

## Control Flow
If no tests are specified, it enumerates `tests/*.img.bz2`. For each test it materializes an image, regenerates native-endian swap images when needed, runs `./tst_probe`, compares output with the expected `.results`, records `.ok` or `.failed`, and exits nonzero if any comparison failed.

## State, Persistence, Dependencies, Risks, and Test Signals
State is stored in `tests/tmp`, `tests/*.out`, `tests/*.ok`, and `tests/*.failed`. Dependencies include compressed fixture images and a host `mkswap`. Risks include host-dependent swap UUID support, native-endian swap output differences, and shell `eval` around optional UUID filtering. Test signals are exact expected-output matches across all fixture filesystem images.
