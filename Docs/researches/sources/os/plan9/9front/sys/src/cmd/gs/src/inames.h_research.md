# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inames.h

Public name-table interface independent of a particular name-table instance. It declares the `names_` API used by the interpreter and memory/GC code.

Key contents:
- Forward-declares `name_table` and defines `name_index_t`.
- Exposes `name_max_string`.
- Declares name table allocation and memory access: `names_init`, `names_memory`.
- Declares name lookup/interning APIs: `names_ref`, `names_enter_string`, and `names_from_string`.
- Documents `names_ref` enter modes: no-enter, static string, copied string, and already dynamically allocated string.
- Defines `names_eq` as pointer equality between interned name objects.
- Declares value-cache invalidation, index/ref conversion, valid-index iteration, GC marking, and subtable object lookup routines.

Notable dependencies:
- Uses Ghostscript `ref`, `name`, `gs_memory_t`, `gs_ref_memory_t`, and `bool` types supplied by surrounding interpreter headers.

Research notes:
- The API separates public name operations from implementation details in `inamedef.h`.
- The name table is tightly integrated with GC relocation because callers can ask for the object/subtable containing a name or name string.
- Name refs are canonicalized, so equality can be tested by comparing `value.pname`.
