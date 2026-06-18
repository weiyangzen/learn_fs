# File Research: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm_test.c

Interactive test driver for `libo2dlm`. It parses stdin commands and exercises domain registration, lock/unlock, trylock, and LVB read/write.

Supported commands are `REGISTER`, `UNREGISTER`, `LOCK`, `TRYLOCK`, `UNLOCK`, `GETLVB`, `SETLVB`, and `HELP`, with case-insensitive parsing. PR locks accept `PR`, `PRMODE`, `RO`, or `O2DLM_LEVEL_PRMODE`; EX locks accept `EX`, `EXMODE`, or `O2DLM_LEVEL_EXMODE`.

`main()` initializes the o2dlm error table, defaults to `/dlm/`, accepts `-u` to use fsdlm (`dlmfs_path = NULL`), or treats the first argument as a dlmfs mount path. The command loop calls the public `o2dlm_*` API and reports errors with `com_err`.

Important limitations: this is a manual/debug tool, not an automated test; it maintains one global `dlm_ctxt`; `UNREGISTER` calls destroy on that context and clears it; LVB operations use a fixed 64-byte buffer.
