# sources/user-network-fs/rclone/cmd/mount/test/seek_speed.go

Purpose: standalone diagnostic tool for measuring random seek/read performance on a single file, intended for mount performance experiments rather than production command behavior.

Important APIs/state: flags `--size` and `--n` configure byte range and iteration count. `randomSeekTest` repeatedly chooses random offsets, seeks, reads one byte, and reports aggregate rate.

Control flow: `main` parses flags, opens the provided file, and runs the benchmark. The test loop uses `math/rand` global source and `time.Since` for throughput.

State/persistence: read-only file access; output to stdout. Dependencies are standard `flag`, `os`, `math/rand`, `time`. Risks include non-cryptographic random, minimal error context, and synthetic one-byte reads that may not represent real workloads. No automated tests.
