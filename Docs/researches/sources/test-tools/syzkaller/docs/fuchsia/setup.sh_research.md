# sources/test-tools/syzkaller/docs/fuchsia/setup.sh Research

## Purpose
This Bash helper sets up, builds, runs, and nominally updates syzkaller for Fuchsia. It expects absolute syzkaller and Fuchsia checkout paths and creates `workdir.fuchsia` under the syzkaller tree.

## Important functions
- `die`, `usage`, and `preflight` handle user errors and check `go`, syzkaller, and Fuchsia directories.
- `build` configures Fuchsia `core.x64` with syzkaller/fuzzing bundles and KASAN, builds it, then builds syzkaller for `TARGETOS=fuchsia TARGETARCH=amd64`.
- `run` locates product bundle images with `ffx`, injects SSH authorized keys into a ZBI, copies FXFS, writes a `syz-manager` JSON config, extends `PATH` for QEMU, and launches `bin/syz-manager`.
- `update_syscall_definitions` is currently a TODO that exits before extraction.

## Control flow
`main` parses optional `-d`, requires exactly three positional arguments, initializes `workdir`, then dispatches `build`, `run`, or `update`; all unknown commands show usage. Strict shell options make most failures abort immediately.

## State and persistence
The script writes `workdir.fuchsia/fx-syz-manager-config.json` and `out/x64/syzdeps` copies inside the Fuchsia checkout. It relies on Fuchsia `fx`/`ffx` state and SSH key config.

## Dependencies and integration points
Depends on Go, Fuchsia `fx`/`ffx`, qemu prebuilts, syzkaller Makefile targets, and Fuchsia product bundle image names. The generated manager config integrates with syzkaller's qemu VM backend.

## Risks
Global variables are intentionally loose per TODOs, absolute path requirements are not deeply normalized, `update` is nonfunctional, and the run path depends on current Fuchsia product config. Writing JSON via shell interpolation assumes paths do not contain problematic characters.

## Test signals
Useful checks are `setup.sh help`, `build` completion, `ffx config check-ssh-keys`, and a successful `syz-manager` launch. This research pass did not run the script.
