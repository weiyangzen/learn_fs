# sources/test-tools/fio/optgroup.h

Purpose: declares option grouping bitmasks and lookup functions for fio options.

Important APIs/types: `struct opt_group`, `enum opt_category`, `enum opt_category_group`, bitmask constants such as `FIO_OPT_C_IO` and `FIO_OPT_G_IOLOG`, invalid sentinels, and lookup prototypes.

Control flow/state: categories are powers of two intended to be combined into `uint64_t` masks. Lookup functions consume masks bit by bit and return descriptors from implementation tables.

Dependencies/integration: requires `uint64_t` from prior includes or translation-unit context; implementation includes `inttypes.h`, but the header itself does not. Used by parser/help code assigning options to categories.

Risks/test signals: enum order and bit assignments are ABI-like within fio help/parser data. Header standalone compilation should be checked because it uses `uint64_t` without including `<stdint.h>`/`<inttypes.h>`.
