# File Research: sources/os/linux/linux/fs/proc/bootconfig.c

## Purpose
Creates `/proc/bootconfig`, exposing extra boot configuration in a normalized text format.

## Main Responsibilities
- Walks bootconfig key/value nodes.
- Composes key names and quoted values into a saved buffer.
- Appends bootloader command-line parameters when extra options are present.
- Registers a single proc file that emits the saved bootconfig buffer.

## Key Interfaces
- `boot_config_proc_show()`
- `copy_xbc_key_value_list()`
- `proc_boot_config_init()`

## Control Flow and Data Handling
At init, the file first calls `copy_xbc_key_value_list(NULL, 0)` to compute required output length, allocates `saved_boot_config`, then calls the same formatter again to fill it. Values are quoted with either double or single quotes depending on embedded quote characters. Empty values are rendered as `""`.

## Dependencies and Integration
Depends on bootconfig parser APIs (`xbc_for_each_key_value`, `xbc_node_compose_key`, array value helpers), `boot_command_line`, seq_file, and procfs creation.

## Risks and Review Hotspots
- Length calculation and formatting share one function; `snprintf` return handling must remain correct.
- Saved output is allocated once at init and intentionally reused for reads.
- Quoting is minimal and tailored to display, not a general parser/serializer contract.
