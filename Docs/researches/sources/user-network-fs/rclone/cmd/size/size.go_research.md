<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/size/size.go -->
# sources/user-network-fs/rclone/cmd/size/size.go

Source read: complete file, 84 lines, 2743 bytes, sha256 `780f08e1b8109d77b2ecb2c771be8bf5e613b7170c470082cf84098be064d452`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/size/size.go_research.md`.

## Purpose
Defines the `rclone size` command to count objects, bytes, and sizeless objects under a remote path.

## Important APIs, types, and functions
`jsonOutput` flag and `commandDefinition` implement CLI registration. Run builds an Fs, calls `operations.Count`, logs sizeless warnings, and prints JSON or human-readable totals.

## Control flow
Execution validates one path, enters `cmd.Run`, collects counts recursively according to global filters/depth, then formats output.

## State and persistence behavior
No remote mutation. Local state is only the command flag and stdout/log output.

## Dependencies and integration points
Depends on command framework, flags, JSON encoder, fs suffix formatting, and operations count.

## Risks and edge cases
Some backends report unknown sizes; the command counts them as empty and warns, so totals may be underestimated.

## Test signals
Covered by operations/count tests outside this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/size/size.go -->
