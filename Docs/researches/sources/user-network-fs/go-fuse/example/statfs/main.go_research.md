# sources/user-network-fs/go-fuse/example/statfs/main.go

Purpose: command-line driver for the benchmark `StatFS` filesystem.

Important flow: parses debug, CPU profile, memory profile, post-mount command, and TTL; reads filenames from an input file; populates `benchmark.StatFS` with regular-file attrs; mounts with attr/entry TTLs; starts CPU profiling after mount; optionally starts a command; waits for unmount; writes heap profile at exit.

State/dependencies: filesystem tree is in memory; optional profile files are persistent artifacts; optional command runs outside the server.

Integration/risks: integrates benchmark package, `fs.Mount`, `runtime/pprof`, and external commands. Risks include `strings.Split` not respecting shell quoting for `-run`, and profile output requiring graceful unmount. Test signal is manual benchmark and build coverage.
