# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/restore_wshadow.hpp

Purpose: Restores GCC `-Wshadow` diagnostics after FOA internals temporarily suppress them.

Important APIs, types, and functions: No runtime API. It defines `BOOST_UNORDERED_DETAIL_RESTORE_WSHADOW`, includes `ignore_wshadow.hpp`, then undefines the marker.

Control flow: The included `ignore_wshadow.hpp` sees the restore marker and emits `#pragma GCC diagnostic pop` under GCC.

State and persistence behavior: Only compiler diagnostic state is affected.

Dependencies and integration points: Paired with `ignore_wshadow.hpp` in `core.hpp` and `concurrent_table.hpp`.

Risks: If included without a prior push on GCC, diagnostic stack handling would be mismatched; current usage pairs it directly after FOA template regions.

Test signals: GCC warning-configuration builds should verify no diagnostic suppression leaks past FOA includes.
