# sources/test-tools/syzkaller/pkg/vcs/linux_configs_test.go

## Purpose

This file tests Linux sanitizer config pruning for different crash types.

## Important APIs, Types, And Functions

`TestDropLinuxSanitizerConfigs` feeds a base config to `setLinuxSanitizerConfigs` and asserts that required configs remain for warnings, KASAN, warning plus KASAN, lockdep, and RCU stall cases. `TestNoDoubleRcuSuppress` ensures the RCU stall suppression command-line parameter is not appended twice. `assertConfigs` checks selected config values.

## Control Flow, State, Dependencies, And Integration

Tests parse in-memory Kconfig data and use `debugtracer.NullTracer`. They inspect `kconfig.ConfigFile` values after mutation.

## Risks And Test Signals

The tests protect high-risk bisection behavior where disabling the wrong instrumentation can hide the bug. They do not cover tag-based config disabling, every crash type predicate, or malformed `CMDLINE` values.
