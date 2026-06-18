# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iparam.h

Header defining interpreter parameter-list structures and constructors for `iparam.c`.

Key contents:
- Includes `gsparam.h`.
- Documents three parameter-list implementations: dictionary objects, name/value pairs in arrays, and name/value pairs on a stack.
- Defines `iparam_loc`, pairing a value ref with the result slot for that parameter.
- Defines `iparam_list_common`, extending `gs_param_list_common` with interpreter ref memory, read/write function pointers, policy/wanted dictionaries, enumeration hook, results array, count, and integer-key mode.
- Defines `iparam_list`, `dict_param_list`, `array_param_list`, and `stack_param_list`.
- Declares constructors for reading and writing dictionaries, indexed arrays, raw arrays, and stacks.
- Defines `iparam_list_release`, freeing the results array.

Notable dependencies:
- Requires interpreter allocation/stack types from `ialloc.h` and `istack.h` in practice, as noted by the file comment.
- `gsparam.h` for generic parameter-list types.

Research notes:
- The read and write modes share the same base structure but use different union members.
- The `results` array is meaningful for read lists; write lists set it to zero.
- `int_keys` changes key conversion from names to decimal integer strings and integer refs.
