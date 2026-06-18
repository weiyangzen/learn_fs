# sources/security-integrity/gocryptfs/tests/reverse/linux-tarball-test.bash

## Purpose
End-to-end reverse-mode smoke test that extracts the Linux 3.0 tarball, mounts it reverse, remounts the encrypted view forward, and verifies the original tree through MD5 checks.

## Important APIs, Types, And Functions
- `../dl-linux-tarball.bash` ensures `/tmp/linux-3.0.tar.gz` exists.
- `gocryptfs -reverse -init`, reverse mount, and forward mount build an `a -> b -> c` chain.
- `md5sum -c` compares against `tests/stress_tests/linux-3.0.md5sums`.

## Control Flow
The script creates a temp workdir under `/tmp`, extracts the kernel tree to `a`, initializes reverse config, mounts `a` on `b`, mounts `b` on `c`, then runs MD5 verification from `c` with `pv` progress and filters OK lines.

## State And Persistence
It creates temp directories and FUSE mounts, cleaned by an EXIT trap using `fuse-unmount -z` and `rm -rf`.

## Dependencies And Integration Points
Depends on shell utilities, tar, md5sum, pv, gocryptfs in PATH, the shared unmount helper, and the Linux tarball checksum fixture.

## Risks And Edge Cases
The test is heavyweight and assumes `/tmp` space plus Linux checksum fixture stability. It does not use the just-built `../../gocryptfs` path explicitly.

## Test Signals
A clean pass means every file in the forward-remounted reverse view matches the known Linux 3.0 MD5 sums.
