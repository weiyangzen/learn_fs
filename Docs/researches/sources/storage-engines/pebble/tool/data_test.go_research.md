## sources/storage-engines/pebble/tool/data_test.go

Purpose: provides the shared datadriven harness for most `tool` package command tests. `runTests` expands a testdata glob, clones referenced on-disk fixtures into a memory filesystem, constructs a top-level Cobra command around `tool.New`, executes datadriven commands, and normalizes output. This file is the integration glue for `db_*`, `find`, `manifest_*`, and `remotecat` tests.

Important APIs and control flow: `runTests(t, path)` registers custom comparer, alternate comparer, merger, Cockroach key schema, custom corruption enhancer, and an in-memory FS. The special `create` datadriven command opens a Pebble DB with the test comparer/merger and `FormatVirtualSSTables`. Other commands are assembled from datadriven command names, args, and input fields, then path-like args are cloned once into memfs so later commands observe mutations. `timeNow` is replaced with a monotonic deterministic clock for scan summaries; `overrideRenderMetricsForDeterminism` swaps `renderMetrics` to `Metrics.StringForTests`.

State and persistence: test fixture state lives in a per-test memfs, but cloned fixture mappings are retained across commands within a test file to preserve DB/catalog/manifest mutations. Global state mutations (`timeNow`, `renderMetrics`) are deferred back to production values.

Dependencies and integration: depends on `datadriven`, `vfs.Clone`, `cobra`, test comparers, `cockroachkvs`, and `New` command construction. It exercises public command wiring rather than calling command handlers directly.

Risks: path cloning is heuristic and only clones args that resolve against the real FS. Global overrides must be restored or later tests become order-dependent. The harness hides stdout/stderr distinction by routing both into one buffer.

Test signals: all thin test files call this helper; output golden files detect command behavior, formatting, option loading, custom comparer/merger handling, corruption enhancer behavior, and deterministic metric rendering.
