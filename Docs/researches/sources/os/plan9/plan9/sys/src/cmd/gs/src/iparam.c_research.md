# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.c

Interpreter-backed implementations of Ghostscript parameter lists. It converts between generic `gs_param_list` reads/writes and PostScript refs stored in dictionaries, arrays, or stacks.

Key behavior:
- Converts parameter keys to refs with `ref_param_key`, supporting name keys or integer keys encoded as decimal strings.
- Converts ref keys back to `gs_param_key_t` with `ref_to_key`.
- Defines write-side list procs for typed values, nested collections, key enumeration, and wanted-key filtering.
- Writes scalar values as refs: null, bool, int/long, float, string, and name.
- Writes arrays by allocating ref arrays and filling integer, float, string, or name elements.
- Writes nested dictionaries and arrays through child `dict_param_list` instances.
- Provides stack-backed writing by pushing key/value pairs on a ref stack.
- Provides dictionary-backed writing via `dict_put`.
- Provides indexed-array writing using integer keys and direct array element assignment.
- Defines read-side list procs for typed values, nested collections, policy lookup, error signaling, and commit.
- Reads arrays as int, float, string, or name arrays, guessing by the first element for generic typed reads.
- Reads strings from either names or readable strings.
- Supports dictionary, array-pair, indexed-array, stack, and empty-collection readers.
- Tracks per-parameter results so commit can enforce `require_all` and mark unqueried parameters as `undefined`.

Notable dependencies:
- Interpreter object and stack APIs: `oper.h`, `opcheck.h`, `istack.h`, `store.h`.
- Dictionary/name APIs: `idict.h`, `iname.h`.
- Generic parameter API: `iparam.h`, `gsparam.h`.

Research notes:
- Read result slots use `0` for untouched, `1` for successful access, and negative error codes.
- Integer-key dictionaries are represented externally as decimal string keys but internally as integer refs.
- `ref_to_key` allocates integer-key strings with GC-managed memory and marks them persistent.
