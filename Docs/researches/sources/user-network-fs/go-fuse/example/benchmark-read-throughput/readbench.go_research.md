# sources/user-network-fs/go-fuse/example/benchmark-read-throughput/readbench.go

Purpose: standalone helper for measuring repeated single-file read throughput.

Important functions: `gulp` opens a file, reads it in blocks until a short read, and returns bytes read; `main` parses block size in KiB and total MB limit, repeatedly calls `gulp`, accumulates duration and MB read, then prints MB/s.

Control flow/state: no persistent state; repeated full-file reads until total MB threshold is reached.

Dependencies/integration: uses standard `os`, `flag`, and `time`; intended to run against mounted FUSE files. Risks include ignoring non-EOF read errors inside `gulp` because it discards the error from `f.Read`, and integer truncation in throughput output. Test signal is manual benchmark output rather than automated tests.
