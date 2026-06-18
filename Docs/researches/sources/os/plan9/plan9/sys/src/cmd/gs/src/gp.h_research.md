# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp.h

Read status: complete.

Purpose: central Ghostscript interface for platform-specific routines. Implementations live in `gp_*.c` files.

Major API areas:
- Initialization and exit: `gp_init`, `gp_exit`, `gp_do_exit`.
- Error and time: `gp_strerror`, `gp_get_realtime`, `gp_get_usertime`.
- Line reading and stdin: `gp_readline_*`, `gp_stdin_read`.
- Display environment: `gp_getenv_display`.
- File constants: name-list separator, scratch prefix, null file name, current directory name, binary-mode suffixes.
- File access: `gp_open_scratch_file`, `gp_fopen`, `gp_setmode_binary`.
- Path combining: `gp_file_name_combine` plus helper callbacks for platform root/separator/current/parent semantics.
- Mac resource access: `gp_read_macresource`.
- Persistent cache: `gp_cache_insert`, `gp_cache_query`, cache type IDs.
- Printer access: `gp_open_printer`, `gp_close_printer`.
- File enumeration: `gp_enumerate_files_init`, `gp_enumerate_files_next`, `gp_enumerate_files_close`.
- Native font enumeration: `gp_enumerate_fonts_init`, `gp_enumerate_fonts_next`, `gp_enumerate_fonts_free`.

Filesystem/storage relevance:
- This is the key abstraction boundary for file naming, scratch files, printer pseudo-files, file enumeration, resource-fork access, and persistent caches.
- Platform implementations in this group fill in DOS, Windows, Mac, OS/2, OS-9, Unix-like, and stub variants.

Notable behavior:
- Comments document platform-specific semantics for roots, separators, parent/current references, and empty path items.
- The misspelled functions `gp_file_name_is_partent_allowed` and `gp_file_name_is_empty_item_meanful` are part of the declared ABI here and mirrored in implementations.
