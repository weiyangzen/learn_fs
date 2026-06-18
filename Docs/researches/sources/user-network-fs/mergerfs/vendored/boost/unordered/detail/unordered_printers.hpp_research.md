# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/unordered_printers.hpp

## Purpose

This generated header embeds Python GDB pretty-printers and xmethods for Boost.Unordered containers into ELF objects through the `.debug_gdb_scripts` section. When enabled, GDB can discover and display Boost unordered maps, sets, flat/open-addressing containers, concurrent containers, iterators, and stats objects without separate Python files.

## Important APIs, types, and functions

The C++ surface is only preprocessor guards plus an `__asm__` block. The embedded Python defines `BoostUnorderedHelpers`, `BoostUnorderedPointerCustomizationPoint`, `BoostUnorderedFcaPrinter`, `BoostUnorderedFcaIteratorPrinter`, `BoostUnorderedFoaPrinter`, `BoostUnorderedFoaIteratorPrinter`, stats printers, and `BoostUnorderedFoaGetStatsMethod`/matcher.

FCA printers traverse classic bucket chains through `table_`, `buckets_`, and node `next` pointers. FOA printers traverse flat/open-addressing arrays using group metadata, occupied masks, sentinel detection, and element pointers. Both map printers yield alternating key/value children; set printers yield index/value pairs.

The xmethod exposes `get_stats` for supported flat/node unordered and concurrent containers, returning `table_.cstats` when the binary was compiled with stats.

## Control Flow

The C++ preprocessor includes the embedded script only when `BOOST_ALL_NO_EMBEDDED_GDB_SCRIPTS` is not defined and the target is ELF. Clang diagnostics are suppressed around the long assembly string.

At debug time, GDB loads the inlined script, builds a `RegexpCollectionPrettyPrinter`, registers template regexes for Boost.Unordered types, and registers an xmethod matcher. Printer `children()` methods are generators that walk container internals until bucket counts, null nodes, occupied masks, or sentinels terminate traversal.

## State and Persistence Behavior

The header adds debug metadata to compiled objects but no runtime data or executable program behavior. In GDB, printer instances hold references to inspected values, table pointers, pointer customization helpers, and derived flags such as `is_map`. The xmethod prints a diagnostic if stats were not compiled in.

## Dependencies and Integration Points

It depends on ELF debug-script support and GDB Python modules `gdb.printing`, `gdb.xmethod`, `re`, and `math`. It is tightly coupled to Boost.Unordered internal layout names such as `table_`, `buckets_`, `arrays`, `groups_`, `elements_`, `size_ctrl`, `buf.t_`, and FOA group metadata. Fancy pointer support integrates with external pretty-printers that implement `boost_to_address` and `boost_next`.

## Risks and Edge Cases

The script is layout-sensitive. Any internal field rename or group representation change can break debugging while normal code still compiles. Optimized builds may omit some constants, so the FOA printer hardcodes `N = 15` and `sentinel_ = 1`. Fancy pointer support depends on optional methods in other printers. The embedded assembly is ELF-specific and disabled elsewhere, so debugger behavior differs by platform. Very large containers can be expensive to expand in GDB.

## Test Signals

Debug tests should compile small programs containing each supported container, load them in GDB, and verify summaries, children, iterator displays, and stats xmethod behavior. Tests should cover classic node containers, flat containers, concurrent containers, maps versus sets, empty and non-empty states, optimized builds, fancy pointer allocators, and builds with `BOOST_ALL_NO_EMBEDDED_GDB_SCRIPTS`.
