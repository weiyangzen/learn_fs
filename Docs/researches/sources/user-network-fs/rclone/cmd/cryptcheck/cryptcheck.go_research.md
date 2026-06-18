<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptcheck/cryptcheck.go -->
# sources/user-network-fs/rclone/cmd/cryptcheck/cryptcheck.go

## Purpose

`cryptcheck.go` implements `rclone cryptcheck`, verifying that a plaintext source matches a crypt remote's encrypted objects by comparing hashes at the underlying encrypted layer.

## Important APIs, Types, and Functions

The command registers shared check report flags. `cryptCheck(ctx, fdst, fsrc)` requires `fdst` to be `*crypt.Fs`, chooses one hash from the underlying Fs, builds `check.GetCheckOpt`, and overrides `opt.Check` to unwrap crypt destination objects, read the underlying hash, compute the expected encrypted hash with `fcrypt.ComputeHash`, and report differences.

## Control Flow

The Cobra command resolves source and crypt destination, then runs `cryptCheck` through `cmd.Run(false, true, ...)`. `operations.CheckFn` performs traversal and invokes the custom comparator.

## State and Persistence Behavior

The command is read-only against remotes but may create local report files through shared check flags.

## Dependencies and Integration Points

It integrates with `backend/crypt`, shared check options, `fs/hash`, and operations check traversal.

## Risks and Test Signals

Risks include panics if destination objects are not crypt objects, no underlying hash support, missing hashes, report writer leakage, and expensive source reads for remote sources. Tests should cover non-crypt destination, no-hash underlying Fs, matching/mismatching objects, report outputs, and hash error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptcheck/cryptcheck.go -->
