# sources/test-tools/syzkaller/pkg/vcs/linux_configs.go

## Purpose

`linux_configs.go` contains rules for disabling Linux kernel config options that break older bisection builds/boots and for removing unneeded sanitizer/instrumentation options based on crash type.

## Important APIs, Types, And Functions

`setLinuxTagConfigs` unsets or alters configs based on reachable release tags, plus always-disabled items such as `LOCALVERSION_AUTO`, `DEBUG_INFO_BTF`, `DEBUG_KOBJECT`, and `BLK_DEV_INITRD`. It can swap `UNWINDER_ORC` to `UNWINDER_FRAME_POINTER`. `setLinuxSanitizerConfigs` maps crash type predicates to sanitizer/config categories and disables those not needed.

## Control Flow, State, Dependencies, And Integration

Both functions mutate a `*kconfig.ConfigFile`. Tag checks disable a config when the required tag is missing; nil tags disable only `disable-always` entries. Sanitizer minimization computes needed categories from `crash.Type` values, applies disablers, and logs disabled groups through `debugtracer`.

## Risks And Test Signals

Rules are historical and can become stale as kernel/toolchain behavior changes. Command-line string editing for `CMDLINE` assumes quoted values and appends RCU stall suppression before the final quote. `linux_configs_test.go` covers key crash-type preservation and duplicate suppression avoidance.
