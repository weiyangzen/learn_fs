# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/dirent.h

Declares compatibility directory APIs using `struct dirent12`.

It maps old `opendir`, `readdir`, `readdir_r`, `_readdir_unlocked`, `scandir`, `getdents`, `alphasort`, and `getdirentries` declarations alongside modern `__*30` variants.

Filesystem relevance is direct: this header preserves old directory-entry ABI for filesystem traversal.
