# sources/user-network-fs/go-fuse/example/virtiofs/main.go

Purpose: serves a loopback filesystem over virtiofs rather than mounting through the normal FUSE mount path.

Important flow: parses args, uses `flag.Arg(0)` as socket path and `flag.Arg(1)` as backing directory, creates `fs.NewLoopbackRoot`, enables debug logging, builds a raw node filesystem with `fs.NewNodeFS`, and calls `virtiofs.ServeFS`.

State/dependencies: backing filesystem persists data; virtiofs server listens on the socket path.

Integration/risks: depends on `virtiofs` package, loopback implementation, and correct argument count. The code does not validate missing args before use. Test signal is build coverage plus virtiofs integration tests driven by `all.bash`.
