<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/server.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/server.go

Purpose: constructs the exported FUSE server by creating the core filesystem and layering cross-cutting wrappers for error mapping, optional tracing, monitoring, and optional notifier support.

Important APIs/types/functions: `NewServer(ctx context.Context, cfg *ServerConfig) (fuse.Server, error)`.

Control flow: `NewServer` calls `NewFileSystem`; wraps the resulting `fuseutil.FileSystem` with `wrappers.WithErrorMapping`; conditionally wraps with `wrappers.WithTracing` if `cfg.IsTracingEnabled`; always wraps with `wrappers.WithMonitoring`; then returns either `fuse.NewServerWithNotifier` or `fuseutil.NewFileSystemServer`.

State and persistence behavior: this file owns no persistent state. Its ordering controls runtime state visibility to instrumentation: monitoring observes errors after inner error mapping and optional tracing have processed calls.

Dependencies and integration points: bridges internal `ServerConfig` and `NewFileSystem` with `jacobsa/fuse` server constructors, wrapper packages, tracing config, metrics handle, and dentry notifier.

Risks: wrapper ordering matters for errno categories and tracing spans. A nil metric or trace handle must be valid for wrapper usage via configuration defaults elsewhere. Notifier presence changes the concrete server constructor.

Test signals: indirectly covered by wrapper tests and tracing integration tests in this subset; many fs integration tests call through the server setup path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/server.go -->
