# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iparam.h

Header for interpreter parameter-list implementations.

Key behavior:
- Includes `gsparam.h`.
- Documents three implementations: dictionary objects, name/value arrays, and name/value stack entries.
- Defines `iparam_loc`, pairing a value ref pointer with its result slot.
- Defines shared `iparam_list_common`, embedding `gs_param_list_common`, ref memory, read/write callbacks, policies/wanted dictionaries, enumerator callback, results array, count, and integer-key flag.
- Defines concrete list structs: `dict_param_list`, `array_param_list`, and `stack_param_list`.
- Declares read/write constructors for dictionary, indexed array, pair array, and stack parameter lists.
- Defines `iparam_list_release` to free the results array.

Research notes:
- The header relies on callers including allocator/stack prerequisites noted in comments.
- The same `dict_param_list` struct is reused for dictionaries and indexed arrays, with `dict` holding either kind of ref.
