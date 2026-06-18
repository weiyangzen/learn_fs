# sources/test-tools/syzkaller/pkg/vcs/testdata/linux/merge_config.sh

## Purpose

This shell script is a test fixture replacing Linux `merge_config.sh` behavior for config minimization tests.

## Important APIs, Types, And Functions

The script expects the production-like invocation `merge_config.sh -m -O outdir baseline kernelAdditionsConfig`. It sets `OUTDIR=$3`, writes the contents of `$4` to `$OUTDIR/.config`, appends `$5`, and exits success.

## Control Flow, State, Dependencies, And Integration

It performs simple filesystem writes through shell redirection and command substitution. It depends on bash and `cat`. Integration is as executable testdata for VCS/Linux config code that needs a merge script without invoking the kernel's full script.

## Risks And Test Signals

The script intentionally ignores most real merge semantics, quoting, and error handling. It is only suitable for tests that need concatenation behavior. If argument positions change in callers, the fixture will silently write wrong content or fail.
