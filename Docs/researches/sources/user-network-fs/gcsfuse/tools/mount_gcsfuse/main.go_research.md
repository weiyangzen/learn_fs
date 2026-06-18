# sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main.go

Purpose: mount(8) helper that translates fstab or mount command invocations into `gcsfuse` CLI arguments and executes gcsfuse.

Important APIs/types/functions: `flagTypes`, `isEquiv`, `findEquivFlag`, `makeGcsfuseArgs`, `parseArgs`, `run`, and `main`.

Control flow: parses mount-helper arguments, maps known gcsfuse boolean/non-boolean options from `-o` strings, ignores mount-only no-op options, passes unknown options through as `-o`, normalizes path-like device values to base bucket names, locates gcsfuse and fusermount, then runs gcsfuse with a restricted environment containing PATH, HOME, and proxy variables.

State/persistence behavior: does not persist files, but starts the real gcsfuse mount process and writes diagnostic output to stderr/stdout.

Dependencies/integration: depends on `cfg.BuildFlagSet`, `internal/mount.ParseOptions`, `pflag`, and the executable finders.

Risks/test signals: option map iteration order is nondeterministic, so tests use element matching. Unknown options are intentionally passed to FUSE, which can fail at runtime if unsupported.
