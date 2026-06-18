# sources/test-tools/kdevops/scripts/kconfig/internal.h

## Purpose
`internal.h` declares internal Kconfig parser/symbol globals shared across implementation files but not intended as the public frontend API.

## Important APIs, Types, And Functions
It defines `SYMBOL_HASHSIZE` as `1U << 14`, declares `sym_hashtable`, and provides `for_all_symbols(sym)` as a hash-table iteration macro. It forward declares `struct menu` and exposes `current_menu`, `current_entry`, `cur_filename`, and `cur_lineno`.

## Control Flow
There is no runtime control flow; the header supplies declarations and iteration macros.

## State And Persistence
It references global parser/menu construction state and the global symbol hash table. The state is in-memory only but feeds all later configuration persistence.

## Dependencies And Integration Points
It includes `hashtable.h` and is included by parser, conf, confdata, and symbol/menu implementation files that need global Kconfig internals.

## Risks And Test Signals
Because it exposes mutable globals, ordering and initialization are important. The symbol hash size affects lookup performance. Test signals are successful parser initialization, symbol lookup coverage, and full config reads/writes after parsing nested Kconfig files.
