# sources/storage-engines/wiredtiger/test/format/config.sh

## Purpose
`config.sh` is the generator for the format configuration schema. It writes `format_config.h` and `format_config_def.c` from one ordered list of configuration records, assigning stable numeric offsets used by `GV`, `GVS`, `TV`, and `TVS` macros.

## Important APIs, Types, And Functions
The script emits the `CONFIG` struct, `C_*` flags, `V_GLOBAL_*` and `V_TABLE_*` offset defines, `V_ELEMENT_COUNT`, and `CONFIG configuration_list[]`. It requires `clang-format` and runs `../../dist/s_clang_format` on the generated files.

## Control Flow
The script first writes the header prefix. It then streams a here-document of configuration entries into `format_config_def.c`. For every line beginning with `{"`, it derives an uppercase tag from the config name, chooses `GLOBAL` or `TABLE` based on `C_TABLE`, appends the generated offset to the C initializer, writes a matching `#define` to the header, and increments the offset counter. It appends the sentinel record and final element count, then formats both generated files.

## State And Persistence Behavior
It overwrites generated files in the current `test/format` directory. The ordering of entries is persistent ABI-like state for format's in-memory `CONFIGV` arrays; reordering without regenerating all dependent code would break offset lookups.

## Dependencies And Integration Points
The generated outputs are included by `format.h` and consumed heavily by `format_config.c` and all workers using `GV`/`TV`. The schema spans backup, checkpoints, compression, disaggregation, transaction, workload, stress, tiered storage, and WiredTiger open settings.

## Risks And Test Signals
Risks include missing `clang-format`, accidental manual edits to generated outputs, mismatched offset order, and incorrect `C_TABLE` flags producing wrong global/table access macros. Signals are deterministic regenerated diffs, successful formatting, and compilation failures if the generated enum names drift from code references.
