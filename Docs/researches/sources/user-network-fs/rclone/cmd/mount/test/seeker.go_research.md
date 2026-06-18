# sources/user-network-fs/rclone/cmd/mount/test/seeker.go

Purpose: standalone correctness/performance tool comparing random seeks and byte reads between two files, useful for validating mounted files against a reference.

Important APIs/state: flags `--size` and `--n`; `randomSeekTest(size, in1, in2, file1, file2)` validates that both files return identical bytes at random offsets.

Control flow: `main` parses two filenames, opens both, and runs `n` random seeks. On seek/read mismatch it panics or exits fatally; on success it prints elapsed time and rate.

State/persistence: read-only file access. Dependencies are standard flag/log/os/rand/time. Risks include one-byte sampling missing larger-range defects and dependence on provided size rather than actual file size. No automated tests.
