# sources/user-network-fs/blobfuse2/cmd/root.go
## sources/user-network-fs/blobfuse2/cmd/root.go

Purpose: defines the top-level `blobfuse2` Cobra command, global version-check behavior, fstab/CLI argument normalization, HTTP transport construction, and the public `Execute` entrypoint.

Important APIs/functions: `rootCmd`, `disableVersionCheck`, `checkVersionExists`, `beginDetectNewVersion`, `VersionCheck`, `ignoreCommand`, `parseArgs`, `getTransport`, and `Execute`. `rootCmd` advertises `common.Blobfuse2Version` and returns a mount suggestion when invoked without a subcommand. `parseArgs` rewrites `os.Args` before Cobra sees them.

Control flow: `Execute` calls `parseArgs(os.Args)`, sets those args on `rootCmd`, executes Cobra, and exits with status 1 on errors. `parseArgs` strips the binary name, asks Cobra to resolve the command, injects `mount` for implicit fstab-style invocations that are not built-in Cobra commands, and splits `-o` comma lists into libfuse options versus blobfuse `--` options. Version checking starts a goroutine, validates the compiled version with `common.ParseVersion`, checks raw GitHub sentinel files for warnings/blocked/latest state, prints warnings to stderr, and may `os.Exit(1)` for blocked versions.

State and persistence: global Cobra command and `disableVersionCheck` flag are process state. Version checks perform outbound HEAD requests and write to stderr/log. No local persistent files are changed.

Dependencies/integration: uses `common` constants/version parsing, `common/log`, Cobra, `net/http`, GitHub raw release metadata, environment-sensitive `http.DefaultTransport`, and `os.Args`.

Risks: version checking is network-dependent and can block command startup up to 8 seconds. `beginDetectNewVersion` can call `os.Exit`, which is hard to test and abrupt. `parseArgs` relies on string-prefix splitting of `-o` options and Cobra command discovery, so new commands or flag forms can affect mount injection.

Test signals: `root_test.go` covers missing command behavior, live sentinel URL checks, older-version detection, invalid URL handling, and fstab argument rewriting.
