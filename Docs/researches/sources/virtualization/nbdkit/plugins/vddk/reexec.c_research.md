# File Research: sources/virtualization/nbdkit/plugins/vddk/reexec.c

Implements Linux re-exec support for the VDDK plugin so VDDK shared-library dependencies can be found through `LD_LIBRARY_PATH`.

Key behavior:
- Global `noreexec` disables the mechanism for debugging.
- Global `reexeced` records the original `LD_LIBRARY_PATH` passed through an internal `reexeced_=` config parameter.
- `reexec_if_needed(prepend)` checks whether `prepend` is already in `LD_LIBRARY_PATH`; if not and not already re-execed, it calls `perform_reexec`.
- `perform_reexec` reads `/proc/self/cmdline`, reconstructs argv, removes original `password=` arguments, preserves already-read password data through an unlinked temporary file and `password=-FD`, appends `reexeced_=<old env>`, sets `LD_LIBRARY_PATH=<prepend>[:old]`, and `execvp`s `/proc/self/exe`.
- Non-Linux-like failure to open `/proc/self/cmdline` is debug-only and returns without re-exec.
- Fatal failures such as allocation/read/write/setenv errors call `exit`.
- `restore_ld_library_path` restores or unsets `LD_LIBRARY_PATH` after re-exec so child processes see the original environment, while VDDK still benefits from loader state captured at process start.

Dependencies:
- Linux `/proc/self/cmdline` and `/proc/self/exe`.
- nbdkit password handling state from `vddk.c`.
- const string vector/string helpers.

Notes and risks:
- Re-exec depends on nbdkit not mutating original argv in memory.
- Password preservation avoids rereading stdin or consumed fds after re-exec.
- `restore_ld_library_path` validates that the environment looks like the plugin-created value before changing it.
