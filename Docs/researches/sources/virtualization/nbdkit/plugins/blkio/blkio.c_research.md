# File Research: sources/virtualization/nbdkit/plugins/blkio/blkio.c

This plugin adapts libblkio block devices to nbdkit. It requires `driver=<DRIVER>`, accepts arbitrary libblkio properties, supports `get=PROPERTY` debug reporting, and forbids direct `read-only` configuration in favor of nbdkit's `-r`. Path properties are converted to absolute paths.

`.open` creates a libblkio instance, sets readonly and pre-connect properties, connects, sets post-connect properties, starts the device, prints requested properties, and optionally allocates/maps a per-handle 64 MiB bounce buffer when `needs-mem-regions` is true. `.get_size` reads `capacity`, and `.block_size` derives constraints from `request-alignment` and `optimal-io-alignment`.

I/O callbacks use queue 0 synchronously: read/write/flush/write-zeroes/discard submit one request and wait for one completion with `blkioq_do_io`. FUA and MAY_TRIM map to libblkio flags. Capabilities for flush, trim, and zero are tied to writability; FUA is native.

Risks and invariants: the plugin serializes requests rather than using libblkio's event model. Bounce-buffer users reject requests larger than 64 MiB. Completion `ret` must be zero; any other value is treated as unexpected failure. Property timing depends on the hard-coded pre-connect property list.
