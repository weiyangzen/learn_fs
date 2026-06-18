# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_exec.c

Read completely: 2993 lines.

Implements NetBSD process image replacement and spawn support: `execve(2)`, `fexecve(2)`, `posix_spawn(2)`, executable format dispatch, exec argument buffering/copyout, VM command execution, credentials and emulation switching, signal trampoline mapping, and dynamic exec format registration.

Core state and initialization:
- `execsw`/`nexecs` is the ordered executable-format switch table, protected by global `exec_lock`.
- `ex_head` stores dynamically registered `struct exec_entry` records.
- `struct execve_data` carries the `exec_package`, path buffers, vnode attributes, argument buffer, ps_strings state, resolved name, signal-code size, argument counts, and copied argument length across exec phases.
- `struct spawn_exec_data` carries prepared exec state, file actions, attributes, parent pointer, child-ready synchronization, error status, and a refcount for `posix_spawn`.
- `exec_init()` initializes the exec lock, exec argument submap/pool, sorts exec handlers by priority, rebuilds the `execsw` array, and recomputes `exec_maxhdrsz`.

Executable lookup and format dispatch:
- `check_exec()` resolves either path-based or fd-based executables, requires a regular vnode with execute access, applies `MNT_NOEXEC`/`MNT_NOSUID`, opens the vnode for read, reads the maximum exec header, runs veriexec and PaX segvguard checks when enabled, sets default VM bounds, then tries each registered exec handler's `es_makecmds()`.
- Handler success is followed by entry-address and data/text size limit checks. Handler failure resets fields that a probe may have modified.
- Script/indirect destructive failures can return early via `EXEC_DESTR`.
- `exec_autoload()` attempts to load native or compatibility exec modules after `ENOEXEC`, depending on whether any exec handlers are already present.
- `exec_makepathbuf()` copies user/kernel paths into a `pathbuf`, converting relative paths to absolute paths via the process cwd.
- `exec_resolvename()` resolves vnode-to-path for `fexecve()` style execution.

Exec load phase:
- `execve_loadvm()` enforces `RLIMIT_NPROC` for SUGID cases, takes `p_reflock` writer to block debugger/procfs references, builds path state, initializes the exec package, enters `exec_lock` as reader, calls `check_exec()`, allocates the NCARGS argument buffer, copies arguments/environment, calculates argument and stack sizes, and returns prepared state.
- `copyinargs()` handles fake interpreter arguments (`EXEC_HASARGL`), `EXEC_SKIPARG`, user argv, and environment strings.
- `copyinargstrs()` fetches argument pointers through an abstract fetch callback, copies strings into the kernel argument buffer, enforces `ARG_MAX`, and emits ktrace argument/environment records.
- `calcargs()` and `calcstack()` account for argc/argv/envp pointers, aux data, ASLR stack gap, signal trampoline, `ps_strings`, and machine stack alignment.

Exec commit phase:
- `execve_runproc()` converts prepared state into the live process image. It kills other LWPs, releases robust futexes and lwpctl state, removes POSIX timers, applies PaX flags, replaces the VM space with `uvmspace_exec()`, records text/data/stack sizing, closes close-on-exec descriptors, resets caught signals, marks `PK_EXEC`, and updates credentials through `credexec()`.
- `credexec()` handles setuid/setgid transitions, requires an argument list for set-id binaries, ensures fd 0..2 are open, drops non-persistent ktrace, updates effective and saved credentials, and updates process master credentials.
- `execve_dovmcmds()` runs loader-provided VM commands, handles relative VM commands, records `p_textvp`, then closes/releases the executable vnode.
- `copyoutargs()` and `copyoutpsstrs()` copy argv/env/aux structures and `ps_strings` into the new user stack.
- The commit path runs exec hooks, initializes machine registers via emulation and format hooks, clears LWP private state, discards PCU state, maps sigcode, notifies `EVFILT_PROC` listeners via `knote_proc_exec()`, switches emulation via `emulexec()`, releases locks, and handles ptrace/stop-on-exec behavior.
- If commit fails after the old image has been destroyed, the non-spawn path exits the process with `SIGABRT`; spawn returns the error through its child path.

Signal trampoline and emulation:
- `exec_sigcode_alloc()` creates/refcounts an anonymous UVM object for an emulation's signal trampoline, maps it writable in the kernel to copy code, then later maps it read/execute into processes.
- `exec_sigcode_map()` chooses a user VA through the emulation's address chooser and maps the trampoline into the new process, recording `p_sigctx.ps_sigcode`.
- `exec_sigcode_free()` drops references and clears the emulation sigobject pointer for the last user.
- `emulexec()` installs emulation root, calls old/new emulation process hooks, updates `p_emul`/`p_execsw`, interns syscall handling, and updates ktrace emulation state.

Exec format registration:
- `exec_add()` rejects duplicate handler triples, allocates `exec_entry` records, allocates sigcode objects for emulations, inserts handlers, and rebuilds `execsw`.
- `exec_remove()` refuses removal while any process uses the target `p_execsw`, removes entries, frees sigcode references, and rebuilds `execsw`.
- `exec_free_emul_arg()` frees loader-provided emulation arguments through the package callback.

Posix spawn:
- `check_posix_spawn()` increments global process count, performs fork authorization, and enforces per-user process limits.
- `sys_posix_spawn()` copies file actions and attributes, calls `do_posix_spawn()`, copies out the child pid, and returns errors through `retval` as NetBSD's syscall convention requires here.
- `posix_spawn_fa_alloc()` copies action arrays and duplicates path strings from user memory; `posix_spawn_fa_free()` releases them.
- `do_posix_spawn()` runs `execve_loadvm()` in the parent first, allocates a U-area and new process, initializes process/LWP structures, copies credentials/fd/cwd/limits/signal state, installs spawn data, creates the child LWP at `spawn_return()`, inserts the child into global process lists, makes it runnable, waits for child-ready status, and coordinates ptrace `PTRACE_POSIX_SPAWN` events.
- `spawn_return()` runs in the child, optionally releases the parent early if it can take `exec_lock` itself and no parent-sensitive attrs/errors require waiting, applies spawn attrs and file actions, then calls `execve_runproc()` with spawn-specific lock ownership. It reports child-side errors to the parent when required or exits 127 for POSIX child-side failure behavior.
- `handle_posix_spawn_attrs()` handles process group, scheduler attributes, reset IDs, signal mask, and default signal actions while temporarily making the child visible as stopped for pid-based operations.
- `handle_posix_spawn_file_actions()` performs open/dup2/close/chdir/fchdir actions in the child before exec commit.

Risks and notes:
- `p_reflock` and `exec_lock` ownership is split between normal exec and spawn paths; spawn has explicit `no_local_exec_lock` handling to support parent-held locks.
- `execve_runproc()` has a point of no return after `uvmspace_exec()`; later failures terminate the old process image rather than restoring it.
- Set-id exec refuses zero-argument execution and forces standard descriptors open before credential changes.
- `copyinargstrs()` relies on `ARG_MAX` remaining within the NCARGS pool allocation.
- `check_exec()` tries all handlers under `exec_lock` and can autoload modules on `ENOEXEC`; loader probe functions must clean up modified package state on failure.
- `posix_spawn()` error reporting intentionally differs depending on whether the parent is still waiting and whether `POSIX_SPAWN_RETURNERROR` was requested.
