# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/runtest.sh

Regression test script for legacy `fdisk`.

Test flow:
- Creates a 4 MiB memory disk with `mdconfig`, using geometry `-x 63 -y 16`.
- Verifies `/dev/${MD}` materializes.
- Registers a trap to destroy the md device on exit or signal.
- Creates a one-sector zero bootcode file named `tmp`.
- Runs `./fdisk -b tmp -I $MD`.
- Checks the resulting first-sector checksum against an expected MD5.
- Runs `./fdisk $MD` and checks its textual output MD5.
- Prints `PASSED` messages or exits with failure.

Risks and constraints:
- Requires FreeBSD `mdconfig`, `dd`, and `md5`.
- Depends on exact output formatting and deterministic MBR layout.
- Creates/removes a local temporary file named `tmp` in the working directory.
