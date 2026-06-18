# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/httpd.c

Implements the Venti server HTTP interface. `httpdinit()` registers handlers for stats, index/storage summaries, XML index export, cache flush/kick/empty controls, graphing, runtime knob setting, logs, disk inspection, debug reads, and proc introspection, then starts a listener process.

`listenproc()` accepts connections and starts `httpproc()` per connection. `httpproc()` parses HTTP requests, dispatches exact or prefix URI handlers, serves static files from `webroot` when no handler matches, flushes responses, and honors close semantics.

Helpers parse query arguments, validate GET/HEAD requests, set content types with chunked HTTP/1.1 output, handle errors/not-found, and serve static files with simple extension-based MIME types.

Operational endpoints expose storage summaries, index layout, arena stats, cache controls, runtime integer settings, graph PNG or text bins, Venti logs, and XML serialization helpers. The `/set` endpoint can mutate global tuning flags such as compression, logging, cache sleeps, scheduler mode, Bloom ignore, sync writes, and icache prefetch.
