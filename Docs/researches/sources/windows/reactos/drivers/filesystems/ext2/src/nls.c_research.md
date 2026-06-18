# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls.c

Driver-level NLS module loader/unloader. It declares init/exit entry points for many Linux-style `nls_table` modules and loads them into the global table registry used by filename conversion.

`Ext2LoadAllNls` clears the global `tables` list, initializes `nls_lock`, always loads UTF-8, then under `FULL_CODEPAGES_SUPPORT` loads Chinese GB2312/Big5 and a broad set of single-byte codepages: ASCII, Windows CP1250/1251/1255, DOS CP437/737/775/850/852/855/857/860/861/862/863/864/865/866/869/874/932/949, EUC-JP, ISO-8859 variants, and KOI8 variants. The code relies on `LOAD_NLS` macros to call each module’s initializer and track return state.

`Ext2UnloadAllNls` unloads the same built-in NLS modules in roughly reverse/dependency-safe order, ending with UTF-8. The file is glue code: actual registration logic is in `nls_base.c`, while conversion tables live in the individual `nls_*` files. One notable quirk is that the unload list uses `UNLOAD_NLS(init_nls_ascii)` and `UNLOAD_NLS(init_nls_cp1250)` for the first two entries while the remaining entries use `exit_nls_*` names.
