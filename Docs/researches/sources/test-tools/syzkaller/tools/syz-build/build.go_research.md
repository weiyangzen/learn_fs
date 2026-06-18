<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-build/build.go -->
# sources/test-tools/syzkaller/tools/syz-build/build.go

## Purpose

Testing wrapper around `pkg/build.Image`.

## Important APIs, Types, and Functions

Flags OS/arch/vm/kernel/make/compiler/linker/ccache/config/sysctl/cmdline/userspace/trace; fills `build.Params`.

## Control Flow

Parses flags, warns if not root, disables sandboxing, reads optional config, builds image into cwd, optionally traces, logs signature/compiler.

## State and Persistence Behavior

Writes build outputs in current dir and optional trace artifacts; sets process env.

## Dependencies and Integration Points

Depends on pkg/build backends, root/image tooling, toolchains, supplied paths.

## Risks and Edge Cases

Running in wrong cwd scatters artifacts; non-root can fail late; test wrapper UX is minimal.

## Test Signals

Run known target with and without trace; verify image and signature logs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-build/build.go -->
