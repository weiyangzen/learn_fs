# sources/user-network-fs/go-fuse/benchmark/Makefile

Purpose: builds external benchmark helpers used by the Go benchmark suite.

Important targets: `all` depends on `cstatfs` and `bulkstat.bin`; `cstatfs` compiles `statfs.cc` with `g++ -O2 -Wall -std=c++0x` and `pkg-config fuse --cflags --libs`; `bulkstat.bin` builds `bulkstat/main.go` and copies the produced binary.

State/persistence: creates local artifacts `cstatfs`, `bulkstat/main`, and `bulkstat.bin`.

Dependencies/integration: used by `all.bash` and `BenchmarkLibfuseHighlevelThreadedStat`/`TestingBOnePass`. Risks are dependency on libfuse development headers, pkg-config naming, and stale binaries if source changes are not rebuilt. Test signal is benchmark build success and subsequent benchmark execution.
