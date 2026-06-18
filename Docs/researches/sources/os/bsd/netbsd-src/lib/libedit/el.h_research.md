# File Research: sources/os/bsd/netbsd-src/lib/libedit/el.h

This is libedit's central internal header. It defines the `EditLine` object and shared editor state structures.

Key definitions:
- Local defaults: `KSHVI`, `VIDEFAULT`, and `ANCHOR`.
- Buffer size: `EL_BUFSIZ` is 1024 wide characters.
- Flag bits: `HANDLE_SIGNALS`, `NO_TTY`, `EDIT_DISABLED`, `UNBUFFERED`, `NARROW_HISTORY`, `NO_RESET`, `FIXIO`, and `FROM_ELLINE`.
- `el_action_t`: command action index type.
- `coord_t`: screen coordinate pair.
- `el_line_t`: current editable line buffer/cursor/last/limit.
- `el_state_t`: input mode, numeric argument, meta-next state, and current/previous command metadata.

`struct editline` aggregates:
- Program name, stdio streams, fds, flags, cursor position.
- Real and virtual display buffers.
- Client data.
- Line and command state.
- Terminal, tty, refresh, prompt, literal, character editor, map, keymacro, history, search, signal, and read submodules.
- Conversion buffers for visual/scratch/legacy APIs.
- Legacy `LineInfo` storage.
- Custom getenv callback.

Integration:
- Includes nearly all internal module headers, making this the core dependency for libedit implementation files.
- Declares `el_editmode()` and `el_init_internal()`.

Risks and notes:
- Many internals are exposed to tests and implementation units through this header.
- Memory allocation macros directly map to libc allocation functions.
