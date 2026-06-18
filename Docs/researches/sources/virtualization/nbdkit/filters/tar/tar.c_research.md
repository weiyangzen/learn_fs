# File Research: sources/virtualization/nbdkit/filters/tar/tar.c

This filter exposes a single regular file embedded inside an underlying tar archive. It requires `tar-entry`, optionally limits scanning with `tar-limit`, and lets users override the `tar` executable path.

The first connection entering `.prepare` calculates the member offset and size under a global mutex. It constructs a shell command running `tar --no-auto-compress -t --block-number -v -f - <entry>`, streams bytes read from the underlying plugin into that subprocess until the tar output file receives data or the scan limit is reached, parses tar's block and size output, and converts the tar block number to the member payload offset.

Per-connection handles copy the resolved offset and size. The filter reports member size, prefixes the export description, and forwards read/write/trim/zero/cache operations with the member offset added. Extents are requested against the underlying archive range, then copied back with offsets translated down.

Risks and invariants: initialization assumes the tar archive is not sparse while scanning. Temporary-file and subprocess failures abort preparation. The code checks offset and size against `INT64_MAX` but does not fully verify that the member lies inside the archive. Global initialization means later connections reuse the first resolved member metadata.
