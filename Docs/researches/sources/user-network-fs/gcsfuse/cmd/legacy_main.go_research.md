# sources/user-network-fs/gcsfuse/cmd/legacy_main.go

## Purpose
`legacy_main.go` contains the mount orchestration path for the gcsfuse CLI. It bridges the resolved `cfg.Config` from Cobra/Viper into storage client creation, FUSE server mounting, daemonization, logging, metrics/tracing/profiler setup, metadata prefetch, kernel parameter application, signal handling, and final mount lifecycle joining.

## Important APIs And Functions
Key constants define mount status messages, dynamic-mount filesystem name, signal wait time, and mount slowness threshold. Helpers include `registerTerminatingSignalHandler`, `getUserAgent`, `getConfigForUserAgent`, `createStorageHandle`, `mountWithArgs`, `populateArgs`, `callListRecursive`, `isDynamicMount`, `fsName`, `forwardedEnvVars`, and `logGCSFuseMountInformation`. The exported command path is `Mount(mountInfo *mountInfo, bucketName, mountPoint string) error`.

## Control Flow And State
`Mount` updates logger format, initializes log files in foreground mode, logs config details, warns about deprecated cache fields, and either daemonizes or mounts in-process. Background mode re-executes the current binary with `--foreground`, forwards selected environment variables, optionally redirects stderr to `<logfile>.stderr`, waits for daemon outcome, and logs slowness. Foreground mode sets up metrics/tracing/profiling, creates a storage handle unless using the fake bucket, mounts via `mountWithStorageHandle`, optionally performs synchronous/asynchronous recursive metadata prefetch for static mounts, signals daemon outcome, applies kernel reader parameters in non-GKE environments, registers SIGINT/SIGTERM unmount handling, waits on `mfs.Join`, and shuts down monitoring exporters.

## Dependencies And Integration
The file depends on cfg, common versioning, logger, monitor, profiler, storage/storageutil, kernelparams, mount internals, canned fake bucket support, daemonize, jacobsa/fuse, unix signals, Viper, and metrics/tracing packages. It integrates command config (`mountInfo`) with storage client options such as protocol, retry policy, auth, DirectPath strategy, HNS, Google library auth, read-stall config, metrics, tracing, HTTP DNS cache, local socket binding, GKE detection, and write config.

## Risks And Test Signals
Risks include environment-forwarding omissions in daemon mode, loss of daemon outcome signaling, accidental duplicate logging, user-agent bitset drift, slowness threshold noise, metadata prefetch failure handling, and signal handler races around externally managed mount points. `cmd/legacy_main_test.go` covers storage handle construction for HTTP/gRPC/GKE, user-agent formatting and config bitsets, recursive list success/failure, dynamic mount naming, and forwarded environment variable inclusion/exclusion/precedence. Full mount lifecycle behavior still depends on integration tests because unit tests avoid real FUSE mounting.
