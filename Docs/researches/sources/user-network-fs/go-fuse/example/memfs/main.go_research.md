# sources/user-network-fs/go-fuse/example/memfs/main.go

Purpose: legacy example mounting the deprecated `nodefs` in-memory filesystem.

Important flow: parses `-debug`, requires mountpoint and backing-prefix args, creates `nodefs.NewMemNodeFSRoot(prefix)`, wraps it in `nodefs.NewFileSystemConnector`, starts a raw fuse server with `fuse.NewServer`, and calls `Serve`.

State/dependencies: stores filesystem data in the old nodefs memory implementation, seeded by prefix behavior from that package.

Integration/risks: illustrates older API surface (`fuse/nodefs`) rather than modern `fs`. Risks include deprecated API drift and no signal handling/cleanup. Build coverage in `go build ./...` is the main test signal.
