# sources/sync-backup/casync/src/meson.build

Purpose: defines the casync source grouping for Meson builds.

Important APIs/types/functions: creates `util_sources`, `libshared_sources`, `libshared` static library, `casync_sources`, conditional FUSE source inclusion, and `casync_http_sources`. The manifest lists core modules such as cache, chunking, compression, encoder/decoder, remoting, stores, hash maps, mempool, notification, parsing, quota, reflink, rm-rf, and siphash.

Control flow/state: build-time state comes from Meson configuration variables such as `HAVE_FUSE`. `libshared` combines common code used by tools and tests; executable-specific sources are separated from reusable modules.

Dependencies/integration: connects source files to top-level Meson targets and the test/fuzz Meson files. Conditional source inclusion must match configuration options and optional library detection.

Risks/test signals: source list drift can silently omit a new module from builds or tests. The tests in `test/meson.build` depend on this library being complete enough to link all helper binaries.

Source research group: `subset-b-009122`.
