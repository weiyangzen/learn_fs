# File Research: sources/os/linux/linux-stable/fs/exec.c

This file is the Linux stable core implementation of `execve()`/`execveat()`. It owns binary-format registration and dispatch, executable opening, argument/environment staging, new-mm construction, credential transition, and the point-of-no-return phase where the current task becomes the new program image.

Key elements:
- Maintains the global `formats` list protected by `binfmt_lock`; `__register_binfmt()` and `unregister_binfmt()` add/remove `struct linux_binfmt` handlers.
- `do_open_execat()` opens an executable with `__FMODE_EXEC`, follows or rejects symlinks according to flags, enforces `noexec`, requires regular files, and denies writes while the executable is active.
- `bprm_mm_init()`, `copy_strings()`, `copy_string_kernel()`, `bprm_stack_limits()`, and `setup_arg_pages()` create and populate the new process stack, enforcing argument limits and stack rlimit derived bounds.
- `search_binary_handler()` probes registered binfmt loaders after `prepare_binprm()` and `security_bprm_check()`. `exec_binprm()` handles interpreter recursion and emits audit/ptrace/proc connector events after success.
- `begin_new_exec()` is the central commit path: computes creds, de-threads, cancels io_uring work, unshares file tables/sighand, installs the new mm, closes close-on-exec descriptors, applies dumpability, commits credentials, and optionally passes an execfd to an interpreter.
- Syscall front ends `execve`, `execveat`, compat variants, and `kernel_execve()` converge on `do_execveat_common()`/`bprm_execve()`.

Important dependencies and contracts:
- Relies on binfmt loaders to call back into `begin_new_exec()` and later `setup_new_exec()`/`finalize_exec()`.
- Security hooks are staged carefully: `security_bprm_creds_for_exec()`, `security_bprm_check()`, `security_bprm_creds_from_file()`, and commit hooks see different phases of the exec.
- `bprm->point_of_no_return` changes failure semantics: failures after this point trigger fatal signal behavior rather than returning normally to old userspace.
- `cred_guard_mutex` and `exec_update_lock` protect ptrace/credential/mm visibility during the transition.
- `AT_EXECVE_CHECK` is supported as a pre-exec check path that stops after credential-preparation security checks without parsing/loading the binary.

Failure/edge behavior:
- Enforces `MAX_ARG_STRINGS`, `MAX_ARG_STRLEN`, pointer-array stack accounting, and NULL-argv normalization by injecting an empty argv[0].
- Detects interpreter loops with a depth limit.
- Handles multithreaded exec by killing other threads and, if needed, adopting the old leader’s TGID.
- `suid_dumpable` sysctl is registered under `fs` when sysctl support is enabled.
