# sources/object-store/minio/cmd/bootstrap-messages.go

This file implements a small in-memory tracer for bootstrap messages. It records early startup trace events and can replay them into MinIO's pubsub trace stream after subscribers become available.

`bootstrapTraceLimit` caps stored events at `4 << 10`. `bootstrapTracer` contains an RW mutex and a slice of `madmin.TraceInfo`. `globalBootstrapTracer` is the package-level recorder. `Record` takes the write lock and appends an event unless the slice length is already greater than the limit. `Events` copies the current slice under a read lock. `Publish` iterates over the copied events and publishes only entries with non-empty messages unless the context is done.

The state is process-local and transient. It is not persisted; its purpose is preserving useful diagnostics from the bootstrap phase before normal tracing infrastructure is fully wired. Integration points are `madmin.TraceInfo`, `madmin.TraceType`, and `pubsub.PubSub`.

Risks are modest but include the off-by-one style limit check (`len > limit` permits one more than the nominal limit), memory growth up to the trace cap, and event loss after the cap is exceeded. There is no test in this subset. Correctness mostly depends on lock discipline and callers using `globalBootstrapTracer` for early events.
