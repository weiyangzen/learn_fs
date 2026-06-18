<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/fops_probe/fops_probe.cc -->
# sources/test-tools/syzkaller/tools/fops_probe/fops_probe.cc

## Purpose

KCOV/kallsyms utility to discover file_operations callbacks reached by basic file actions.

## Important APIs, Types, and Functions

Functions `read_kallsyms`, `probe_callback`, `should_skip`, `failf`; uses `/proc/kallsyms`, `/sys/kernel/debug/kcov`, KCOV ioctls, mmap, ioctl/read/write/mmap probes.

## Control Flow

Opens target file, loads text symbols, enables KCOV, probes ioctl/mmap/write/read, maps PCs to nearest symbols, starts at VFS entrypoints, deduplicates/filter noisy symbols, prints callback chain.

## State and Persistence Behavior

Uses KCOV shared memory and local symbol map only; no regular-file writes.

## Dependencies and Integration Points

Requires root/debugfs, KCOV, readable kallsyms, target file safe for simple ops.

## Risks and Edge Cases

Symbol mapping is approximate; target operations can have side effects; single-process diagnostic only.

## Test Signals

Build static and run on a controlled device/driver, verifying expected callbacks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/fops_probe/fops_probe.cc -->
