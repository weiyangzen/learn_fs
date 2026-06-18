# File Research: sources/virtualization/nbdkit/filters/noparallel/noparallel.c

This filter reduces nbdkit's thread model at runtime. Configuration key `serialize` / `serialise` accepts `requests` (default, `SERIALIZE_REQUESTS`), `all_requests` / `all-requests`, or `connections`.

The `.thread_model` callback returns the configured model without consulting `next_thread_model`, relying on nbdkit's runtime thread-model reduction. There is no per-connection state and no I/O callback interception.

The behavioral impact is global concurrency reduction for the filter stack. This is useful for unsafe plugins or filters, but can sharply reduce throughput if set more restrictively than necessary.
