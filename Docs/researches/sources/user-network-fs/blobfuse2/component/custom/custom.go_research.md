# sources/user-network-fs/blobfuse2/component/custom/custom.go

## Purpose

`custom.go` loads external Blobfuse components from Go plugins listed in `BLOBFUSE_PLUGIN_PATH` and registers them with the internal component registry.

## Important APIs, Types, and Functions

The main function is `initializePlugins`; package `init` calls it and exits the process on failure. Plugins must export `GetExternalComponent` with the exact signature `func() (string, func() exported.Component)`.

## Control Flow

`initializePlugins` reads `BLOBFUSE_PLUGIN_PATH`, returns nil when empty, splits a colon-separated path list, skips non-`.so` entries with an error log, opens each `.so` with `plugin.Open`, looks up `GetExternalComponent`, type-asserts the symbol to the expected function signature, calls it to obtain component name and constructor, and registers the component via `internal.AddComponent`.

## State and Persistence Behavior

State changes are process-global: loaded plugins remain in the Go plugin runtime and successful components are added to the Blobfuse component registry. On init failure the package logs, prints a message, and terminates the process with `os.Exit(1)`.

## Dependencies and Integration Points

The file depends on standard `plugin`, `os`, `strings`, `time`, and Blobfuse `log`, `exported`, and `internal` packages. It is the dynamic extension point for out-of-tree components.

## Risks and Edge Cases

Go plugins are version- and build-configuration-sensitive. Any invalid `.so`, missing symbol, or wrong signature aborts startup through package init. Non-`.so` entries are skipped rather than returned as errors. `strings.SplitSeq` means empty segments may be iterated depending on environment string shape.

## Test Signals

`custom_test.go` covers empty plugin path and invalid `.so` path. The disabled valid-plugin test documents known Go plugin package-version issues.
