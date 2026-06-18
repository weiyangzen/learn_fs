# File Research: sources/os/bsd/freebsd-src/sbin/newfs/runtest00.sh

Small regression script for UFS `newfs`. It creates malloc-backed md devices of multiple sizes, labels each, runs `./newfs -R`, and prints an MD5 hash of the resulting partition.

Key behaviors:
- Tests sizes: `1m`, `4m`, `60m`, `120m`, `240m`, `1g`.
- Uses fixed md unit `99`.
- Always attempts cleanup with `mdconfig -d`.
- `-R` ensures deterministic output suitable for hash comparison.

Research notes:
- This validates reproducibility across filesystem sizes, not functional mount behavior.
