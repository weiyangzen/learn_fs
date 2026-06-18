# sources/user-network-fs/samba/source3/client/clitar_proto.h

## Purpose
`clitar_proto.h` declares the public interface of the smbclient tar extension while keeping `struct tar` opaque to callers. It lets `client.c` and other command-dispatch code configure and invoke tar behavior without depending on the full implementation layout in `clitar.c`.

## Important APIs, Types, And Functions
- Forward declaration `struct tar` hides the mutable tar context fields.
- `cmd_block()`, `cmd_tarmode()`, `cmd_setmode()`, and `cmd_tar()` are command callbacks used by the smbclient command table. `cmd_setmode()` is declared here but not implemented in `clitar.c`, so its definition must come from another compilation unit or generated prototype compatibility.
- `tar_parse_args()` parses tar flags and values into a context.
- `tar_process()` executes a prepared context.
- `tar_to_process()` reports whether parsing produced runnable state.
- `tar_get_ctx()` exposes the global tar context pointer.

## Control Flow
The header supports two call styles: interactive command callbacks invoke parsing and processing from command text, while higher-level command-line startup can call `tar_get_ctx()`, `tar_parse_args()`, check `tar_to_process()`, and later call `tar_process()`.

## State And Persistence
No state is stored in the header. It defines access to implementation-owned global state through an opaque pointer. Callers must respect that the context's lifetime and memory ownership are controlled by `clitar.c`.

## Dependencies And Integration Points
The prototypes depend on `TALLOC_CTX`, `bool`, and Samba's common include environment. They integrate with smbclient's command table and with the libarchive/no-libarchive conditional implementation in `clitar.c`.

## Risks
The declaration of `cmd_setmode()` without a visible implementation in the paired source can hide link-time or stale API issues. Because `struct tar` is opaque, misuse is limited, but callers still share one global context and can race or overwrite state if used outside the intended single-threaded smbclient flow.

## Test Signals
Build tests should cover both `HAVE_LIBARCHIVE` and non-libarchive configurations and verify all declared callbacks resolve. CLI tests should exercise command-line and interactive tar flows through these declarations.
