# sources/user-network-fs/go-fuse/example/zipfs/main.go

Purpose: command-line driver for mounting a ZIP archive as a read-only filesystem.

Important flow: parses debug, CPU profile, memory profile, post-mount command, and TTL; creates root with `zipfs.NewArchiveFileSystem`; mounts with attr/entry TTLs; starts optional CPU profiling and command; waits; writes heap profile on exit.

State/dependencies: archive contents are the source of filesystem data; optional profile files are generated.

Integration/risks: integrates `zipfs`, `fs.Mount`, pprof, and external command execution. Risks include `strings.Split` command parsing, memory use for archive metadata, and profile files only being complete after graceful unmount. Test signal is build coverage and manual archive mount behavior.
