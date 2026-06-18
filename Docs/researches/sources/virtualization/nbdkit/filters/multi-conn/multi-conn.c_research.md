# File Research: sources/virtualization/nbdkit/filters/multi-conn/multi-conn.c

This filter controls and emulates NBD multi-connection consistency. Configuration accepts `multi-conn-mode` (`auto`, `emulate`, `plugin`, `disable`, `unsafe`), `multi-conn-track-dirty` (`conn`, `fast`, `off`), and optional grouping by export name through `multi-conn-exportname` / `multi-conn-export-name`.

Runtime state is organized into `handle` objects for active connections and `group` objects for sets of connections that should be flushed together. A global mutex protects group membership and dirty-state updates that must be coordinated. `AUTO` resolves in `.prepare`: if the backend advertises multi-conn, the filter delegates to the plugin; otherwise it emulates by requiring backend flush support. `.get_ready` disables auto emulation under `SERIALIZE_CONNECTIONS`.

I/O wrappers mark dirty state on reads, cache requests, writes, zeroes, and trims. FUA writes/zeroes/trims in emulation mode are downgraded to ordinary operations followed by a coordinated flush. `multi_conn_flush` is the central consistency operation: in emulation mode it flushes all dirty peer connections in the group; otherwise it may skip flushes if dirty tracking says the image is clean, or clear dirty state after a successful backend flush.

Behavioral risks center on dirty tracking precision. `CONN` is more accurate but tracks read/write state per connection; `FAST` tracks only group write dirtiness; `OFF` always flushes broadly. The code deliberately avoids locking in `mark_dirty`, relying on NBD client ordering around flush responses, so misuse by clients issuing flushes concurrently with dependent commands can produce races outside the filter's guarantees.
