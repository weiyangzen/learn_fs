# sources/test-tools/syzkaller/tools/syz-testbuild/testbuild.go

## Purpose
`syz-testbuild` validates that a kernel config and syzkaller bisection environment can build and boot the current kernel plus previous release tags, protecting bisection workflows from config/toolchain regressions.

## Important APIs, types, and functions
- Flags configure target OS/arch, kernel checkout, config/sysctl/cmdline/userspace/bisect binaries, built syzkaller path, sandbox settings, compiler/linker choices.
- Constants `vmType=qemu` and `numTests=5` define the VM backend and boot/test repetitions.
- `main` requires root, constructs a temporary manager config and `instance.Env`, discovers previous release tags through `vcs.Bisecter`, reads kernel config, tests HEAD and each tag.
- `test` builds the commit-specific bisection environment, cleans/builds kernel, runs VM tests, logs verdicts, and saves failure output.
- `saveLog` writes non-empty failure logs as `<hash>.<idx>` in the current directory.

## Control flow
The tool disables syzkaller sandboxing, creates a temp workdir, completes manager config, opens a VCS repo/bisecter, gets HEAD and previous release tags, then iterates. Each commit obtains compiler/config from `EnvForCommit`, cleans/builds the kernel, and either records build failure output or runs five VM tests. Verdicts are collapsed when all runs match.

## State and persistence behavior
It mutates the supplied kernel checkout by switching commits and cleaning/building in tree. It creates and removes a temporary syzkaller workdir. It writes failure logs in the current working directory and relies on root privileges for image creation.

## Dependencies and integration points
Integrates `pkg/vcs` bisection APIs, `pkg/instance` build/test environment, `pkg/mgrconfig`, QEMU VM configuration, and syzkaller build artifacts. Intended for dashboard/kernel config maintenance.

## Risks and edge cases
The tool is destructive to the kernel checkout state and must run as root. It assumes `repo` implements `vcs.Bisecter` with a direct type assertion. `errors.AsType` use depends on local errors helper API. Saved log filenames use commit hash and run index in the current directory, which can collide across runs. Userspace/toolchain paths are not explicitly validated before build.

## Test signals
No direct tests. Real value is integration testing with throwaway kernel checkouts. Unit seams could fake `instance.Env` and `vcs.Bisecter` to test verdict classification and log saving.
