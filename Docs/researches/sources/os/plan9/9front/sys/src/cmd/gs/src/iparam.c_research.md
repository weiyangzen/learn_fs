# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.c

Interpreter-side implementations of Ghostscript parameter-list APIs. It bridges PostScript refs, dictionaries, arrays, and stacks to the generic `gs_param_list` interface used by devices, operators, filters, and configuration code.

Key behavior:
- Converts parameter keys between `gs_param_name` strings and PostScript refs, supporting both name keys and integer keys.
- Converts name/int refs back into `gs_param_key_t` for enumeration.
- Defines generic write procedures for scalars, strings, names, arrays, dictionaries, integer-key dictionaries, and nested collections.
- Writes parameters to dictionaries, indexed arrays, or stacks depending on the concrete list type.
- Honors a wanted-key dictionary during parameter writing, skipping unrequested keys.
- Allocates arrays for typed array writes and fills refs using type-specific helpers.
- Copies non-persistent strings into interpreter memory and stores persistent strings as foreign read-only strings.
- Writes name values through `name_ref`.
- Defines generic read procedures for typed values, nested collections, arrays, policy lookup, error signaling, commit, and key enumeration.
- Reads int, float, string, and name arrays from PostScript arrays or packed arrays.
- Guesses array parameter type from the first element when reading generic typed values.
- Reads dictionaries and detects integer-key dictionaries by enumerating keys.
- Tracks per-parameter results in a `results` array: untouched, successful, or error code.
- Supports `require_all`, where commit marks unread parameters as `e_undefined`.
- Provides concrete readers for empty collections, indexed arrays, name/value arrays, stacks, and dictionaries.
- Provides concrete writers for stacks, dictionaries, and newly allocated indexed arrays.

Notable dependencies:
- Parameter API: `gsparam.h` through `iparam.h`.
- Interpreter data APIs: `oper.h`, `opcheck.h`, `ialloc.h`, `idict.h`, `imemory.h`, `iname.h`, `istack.h`, `iutil.h`, `ivmspace.h`, and `store.h`.

Research notes:
- This file is shared interpreter plumbing, not a device-specific implementation.
- The write path stores only requested keys when a wanted dictionary is present.
- The read path intentionally records individual parameter errors so callers can inspect detailed results and policy decisions.
- Integer-key support is used for array-like parameter collections and integer-key dictionaries.
- Some allocations for read arrays are marked persistent and rely on the parameter-list memory lifecycle or GC rather than immediate caller-owned freeing.
