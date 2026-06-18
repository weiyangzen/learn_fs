# sources/test-tools/fio/t/zbd/run-tests-against-nullb

## Purpose
`run-tests-against-nullb` orchestrates repeated runs of `t/zbd/test-zbd-support` against many synthetic `null_blk` layouts. It creates conventional, fully zoned, mixed conventional/sequential, zone-capacity-limited, max-open-limited, and max-active-limited configurations.

## Important APIs, Types, and Functions
`cleanup_nullb()` removes configfs nullb devices and unloads/reloads `null_blk`. `create_nullb()` loads the module with `nr_devices=0` and creates `/sys/kernel/config/nullb/nullb0`. `configure_nullb()` writes configfs attributes including block size, size, memory backing, zoned mode, zone size/capacity, conventional-zone count, max open, max active, and optional badblock controls. `show_nullb_config()` prints the active test layout.

`section1()` through `section25()` define the layout matrix. CLI options choose sections, individual test cases, max-open limits, repeat count, write-zone-remainder mode, quit-on-error behavior, list-only mode, and cleanup.

## Control Flow and State
The script discovers feature support from `/sys/kernel/config/nullb/features`, then loops over runs and selected sections. Each section resets globals such as `conv_pcnt`, `zone_size`, `zone_capacity`, `max_open`, and `max_active`, configures nullb, prints the layout, and invokes `./test-zbd-support` with accumulated options against `/dev/nullb0`.

## Dependencies and Integration Points
It requires root-level module and configfs access, the Linux `null_blk` module, and the sibling `test-zbd-support` script. Feature detection controls whether unsupported zone-capacity, conventional-zone, or max-active sections are skipped.

## Risks and Test Signals
Risks include destructive interaction with existing null_blk devices, module unload failure, configfs attribute drift across kernels, and global shell state leaking between sections. Signals are section output, skipped unsupported sections (`rc == 2`), child test return codes, total elapsed time, and optional early stop with `-q`.
