# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.h

Header for the UDF wide-character getopt implementation.

Key responsibilities:
- Defines `BAD_OPTION` as the invalid-option return code.
- Defines `optarg_ctx`, the caller-owned state object for reentrant option parsing.
- Defines `struct option` for long-option declarations.
- Defines `no_argument`, `required_argument`, and `optional_argument`.
- Declares `getopt_init()`, `getopt()`, `getopt_long()`, `getopt_long_only()`, and `_getopt_internal()`.

Important behavior:
- `optarg_ctx` stores public parser outputs (`optarg`, `optind`, `opterr`, `optopt`) and internal scan/permutation state (`nextchar`, `first_nonopt`, `last_nonopt`).
- All parser strings are `WCHAR` based; this is not a drop-in byte-string POSIX getopt.
- The comments document GNU-style argument permutation and long-option semantics.

Dependencies:
- Requires `WCHAR` and C linkage support from surrounding includes.
- Implemented mostly by `getopt.cpp`; `getopt_long_only()` is declared but absent in the read implementation file.

Notable risks:
- Consumers expecting standard global `optarg`/`optind` variables must use `optarg_ctx` fields instead.
- `BAD_OPTION` is `'\0'`, which is unusual compared with standard `'?'` behavior and can affect callers that test return values loosely.
