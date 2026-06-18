# sources/user-network-fs/go-fuse/benchmark/benchmark.go

Purpose: small utility support for benchmark code.

Important APIs: `ReadLines(name string) []string` reads an entire file, splits on newline with `bytes.Split`, filters empty lines, and returns strings. On read failure it calls `log.Fatal`.

Control flow/state: no retained state; all data is local to the read. The fatal-on-error behavior is acceptable for benchmark helpers but would be too abrupt for reusable library code.

Dependencies/integration: used by stat filesystem benchmarks and example/statfs to consume path-list inputs. Risks include memory use for very large path lists because the whole file is loaded, and no trimming of whitespace except newline splitting. Test signal is indirect through `stat_test.go` and example benchmark paths.
