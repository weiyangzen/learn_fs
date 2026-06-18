# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerStarter.java

## Purpose
`OzoneManagerStarter` is the Picocli/GenericCli entry point for starting, initializing, upgrade/downgrade prepare cancellation, and bootstrapping an Ozone Manager process.

## Important APIs, types, and functions
- `main` disables JVM network address caching if configured, then runs the command with `OMStarterHelper`.
- `call()` handles plain `ozone om` by running common initialization and starting OM.
- `--init` calls `receiver.init(conf)` and fails if OM init returns false.
- `--upgrade`/`--downgrade` calls `receiver.startAndCancelPrepare(conf)` to remove local prepare state before starting.
- `--bootstrap [--force]` initializes storage, chooses `BOOTSTRAP` or `FORCE_BOOTSTRAP`, and starts OM in bootstrap mode.
- `commonInit()` loads `OzoneConfiguration` and prints the startup/shutdown banner.
- `OMStarterHelper` creates real `OzoneManager` instances and delegates lifecycle operations; it also registers a shutdown hook for normal start.

## Control flow
The CLI path always calls `commonInit()` before invoking a receiver operation. Normal start creates OM, calls `start()`, and leaves it running with a shutdown hook that stops and joins it. Bootstrap initializes storage first, then creates an OM with the selected startup option in try-with-resources, starts it, and joins. Upgrade/downgrade creates OM, cancels prepare state before serving, starts, and joins.

## State and persistence behavior
The starter itself only stores `conf` and an injected receiver. It triggers persistent effects through `OzoneManager.omInit`, security initialization, prepare marker deletion via `cancelPrepare`, bootstrap Ratis configuration changes, and normal OM lifecycle. The shutdown hook stops runtime services but does not create commits or external state beyond normal OM persistence.

## Dependencies and integration points
It integrates Picocli, `GenericCli`, HDDS version provider, `HddsServerUtil.startupShutdownMessage`, `OzoneNetUtils`, `ShutdownHookManager`, and `OzoneManager`. The `OMStarterInterface` injection boundary is the primary test seam.

## Risks and edge cases
Bootstrap force mode intentionally skips remote config validation and can crash existing OMs if configs are stale. `startAndCancelPrepare` cancels local marker state before start; operators must use it consistently across OMs during upgrade/downgrade to avoid divergence as described in `OzoneManager`. Normal `start` does not call `join()` directly and relies on non-daemon server threads plus shutdown hook behavior.

## Test signals
Tests should verify subcommand dispatch, receiver injection, startup banner arguments, init failure handling, force/non-force bootstrap option selection, shutdown hook stop/join behavior, and upgrade/downgrade cancellation ordering before OM start.
