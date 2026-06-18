# sources/user-network-fs/rclone/lib/buildinfo/snap.go

## Purpose
This tiny build-tag-gated file records that the binary was built as a Snap package.

## Important APIs, types, and functions
- The file is compiled only with the `snap` build tag.
- `init()` appends `"snap"` to the package-level `Tags` slice.

## Control flow
During package initialization, the build tag causes this file to participate in the build and its `init` function mutates `Tags`. Later `GetLinkingAndTags` includes this tag in sorted build-tag output.

## State and persistence behavior
The only state change is in-process initialization of `buildinfo.Tags`. There is no persistent state.

## Dependencies and integration points
It depends on `tags.go` defining `Tags`. It integrates with packaging/version display logic that reports build tags.

## Risks and edge cases
The correctness depends entirely on build tooling passing the `snap` tag. If omitted, Snap builds will not self-identify. If other init functions also append tags, final ordering is handled later by sorting.

## Test signals
No local tests are present; validation is build-configuration based.
