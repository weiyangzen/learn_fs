# sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/hazard_pointers.py

## Purpose
`hazard_pointers.py` registers GDB commands for inspecting WiredTiger hazard pointers across threads. It helps identify active sessions holding references that can block eviction or page lifecycle transitions.

## Important APIs and classes
Module-level aliases `SESSION_IMPL_PTR` and `CONN_IMPL_PTR` resolve GDB types. `find_sessions` walks all inferior threads and stack frames looking for an argument named `session`. Command classes `dump_hazard_pointers` and `find_hazard_pointer_for` register `dump_hazard_pointers` and `find_hazard_pointers_for`.

## Control flow and behavior
`find_sessions` saves the original frame, switches through every thread, walks older frames until `info arg session` returns a pointer-like value, records the thread global number and session pointer, then restores the original frame. `dump_hazard_pointers` prints every non-null hazard pointer for active sessions. `find_hazard_pointers_for` validates a single hex pointer argument and prints threads/sessions whose hazard array has a matching `ref`.

## State, dependencies, and integration
The script depends on GDB Python APIs and WiredTiger debug types `WT_SESSION_IMPL` and `WT_CONNECTION_IMPL`. It assumes session frames expose an argument named `session` and that session hazard fields are named `active`, `hazards.inuse`, and `hazards.arr`. It is imported by `load_gdb_scripts.py`.

## Risks and test signals
Risks include GDB command parsing via text output from `info arg session`, stale type/field names after WiredTiger structure changes, and frame restoration failures if GDB state changes unexpectedly. Signals are command registration, session/thread listings, hazard pointer dumps for active sessions, and precise identification of holders for a target `WT_REF` address.
