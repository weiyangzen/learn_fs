<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/mount_helper_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/mount_helper_test.go

## Purpose

This suite tests the OS mount helper binaries (`mount_gcsfuse`, `mount.gcsfuse`, and Linux `mount.fuse.gcsfuse`) using a canned bucket. It validates helper argument parsing, option filtering, read-only mode, relative mount points, mode options, implicit dirs, and fuse subtype support.

## Important APIs, Types, and Functions

`MountHelperTest` is an ogletest suite with `helperPath` and temp `dir`. Helpers `mountHelperCommand` and `mount` execute the helper with PATH set to the built gcsfuse binary directory. Tests include `BadUsage`, `NoMtabFlag`, `SuccessfulMount`, `RelativeMountPoint`, `ReadOnlyMode`, `ExtraneousOptions`, `LinuxArgumentOrder`, `FuseSubtype`, `ModeOptions`, and `ImplicitDirs`.

## Control Flow

Setup selects helper path by OS. Bad usage checks too few/many args and trailing `-o`. Mount tests invoke helpers with canned bucket and temp dir, then inspect files or write failures. Option tests ensure `-n` is ignored, mount-style noise options are filtered, Linux `-o ro` at the end works, mode options map to file/dir modes, and implicit dirs are visible when requested.

## State and Persistence Behavior

Each test mounts a canned filesystem at a temp directory and unmounts it after validation. No persistent remote state is used. Helper path changes temporarily for Linux fuse subtype.

## Dependencies and Integration Points

It depends on the build layout from `main_test.go`, canned fake bucket data, `tools/util.Unmount`, ogletest/matchers, and OS-specific mount helper naming conventions.

## Risks and Test Signals

Helper output strings and mount option parsing behavior are tightly asserted. Passing signal is successful helper-mediated mounting and correct translation/filtering of mount-style options into gcsfuse behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/mount_helper_test.go -->
