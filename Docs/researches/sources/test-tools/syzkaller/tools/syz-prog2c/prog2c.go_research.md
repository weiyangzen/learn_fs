# sources/test-tools/syzkaller/tools/syz-prog2c/prog2c.go

## Purpose
`syz-prog2c` converts a serialized syzkaller program into generated C source, optionally builds it, and supports toggling csource execution features.

## Important APIs, types, and functions
- Flags select target OS/arch, input `-prog`, build mode, threading/repetition/process count/slowdown, sandbox settings, segv/tmpdir/trace/leak, feature enable/disable flags, strict parsing, and optional `vmlinux` for kfuzztest dynamic targets.
- `main` parses feature flags with `csource.ParseFeaturesFlags`, loads target metadata, optionally activates kfuzz targets, deserializes the program, creates `csource.Options`, calls `csource.Write` and `csource.Format`, writes source to stdout, and optionally calls `csource.Build`.

## Control flow
The tool requires `-prog`; usage also prints available feature flags. Program parsing defaults to non-strict unless `-strict` is set. Feature booleans from `ParseFeaturesFlags` are mapped field-by-field into `csource.Options`, with `CallComments` always true. Build mode creates a temporary binary through `csource.Build`, removes it, and reports success on stderr.

## State and persistence behavior
It reads the input program and optional vmlinux. It writes C source to stdout. In build mode it creates and removes a binary from the csource build path. It otherwise has no persistent state.

## Dependencies and integration points
Integrates `prog` serialization, `pkg/csource` C emission/building, `pkg/kfuzztest` dynamic target activation, and blank `sys` imports for target registration. Generated C is used for standalone reproducer workflows.

## Risks and edge cases
Feature flag names must match `csource` feature keys; missing or renamed features would panic through map access only if absent entries are not returned. Build success depends on host compiler/toolchain and target support. Non-strict parsing is permissive by default, which helps old programs but can hide malformed input.

## Test signals
No direct tests. Existing csource/prog tests cover most behavior. Wrapper tests should verify required `-prog`, strict parse failures, feature mapping, kfuzz activation failures, and build cleanup.
