# sources/test-tools/syzkaller/pkg/debugtracer/debug.go

This package defines a small tracing abstraction used by syzkaller components that need optional debug logging or artifact capture. The interface is `DebugTracer` with `Logf` and `SaveFile`.

Implementations are `GenericTracer`, `TestTracer`, and `NullTracer`. `GenericTracer` writes formatted log lines to an `io.Writer`, optionally prefixing timestamps in `02-Jan-2006 15:04:05` format, and saves named files under `OutDir` when configured. `TestTracer` forwards logs to `testing.T.Logf` and leaves file saving unimplemented. `NullTracer` drops both logs and saved files.

State is minimal: writer, output directory, timestamp flag, or test handle. Persistence occurs only through `GenericTracer.SaveFile`, which ensures `OutDir` exists and writes a file with `osutil.WriteFile`. Dependencies are standard formatting/time/path APIs plus `osutil`.

Integration points are callers that want debug traces without hard-coding test or filesystem behavior. Risks include ignoring write errors from `MkdirAll`/`WriteFile`, filename path traversal if untrusted names are supplied, nil `TraceWriter` panics, and no-op `SaveFile` behavior in tests hiding artifact expectations. There are no direct tests in this file, so confidence comes from simple implementation and downstream use.
