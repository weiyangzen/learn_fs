# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_hook.c

Read completely: 742 lines.

Implements NetBSD's generic hook infrastructure and several concrete hook families: shutdown, mountroot, root-spec resolution, exec, exit, fork, critical polling, deprecated power hooks, and dynamically allocated simple hook lists with safe disestablishment while callbacks are running.

Generic hook descriptors:
- `struct hook_desc` stores a callback, argument, and list linkage.
- `hook_establish()` lazily initializes hook locks, allocates a descriptor, optionally takes a writer rwlock, and inserts the hook.
- `hook_disestablish()` optionally takes a writer rwlock, validates membership in diagnostic builds, removes the descriptor, and frees it.
- `hook_destroy()` frees an entire simple linear list.
- `hook_proc_run()` runs process callbacks under an optional reader rwlock and casts the stored callback to the process-hook signature.

Process lifecycle hooks:
- `exechook_establish()`/`exechook_disestablish()` register callbacks protected by `exec_lock`; `doexechooks()` asserts `exec_lock` is held and runs callbacks without taking it again.
- `exithook_establish()`/`exithook_disestablish()` use `exithook_lock`; `doexithooks()` runs exit callbacks under a reader lock.
- `forkhook_establish()`/`forkhook_disestablish()` use `forkhook_lock`; `doforkhooks()` runs callbacks with child and parent proc pointers under a reader lock.

Boot and shutdown hooks:
- Shutdown hooks are removed from the list before invocation in `doshutdownhooks()` so they do not run twice; the code deliberately does not free hook descriptors during shutdown.
- Mountroot hooks map a root device to a callback and include establish/disestablish/destroy/run helpers.
- Root-spec hooks register prompt prefixes and callbacks that translate strings such as wedge names to devices. Establish/disestablish require cold boot or `kernconfig` lock; lookup and printing run under `kernconfig_lock()`.

Other hook families:
- Critical polling hooks are a simple list run by `docritpollhooks()`.
- Power hooks store a name, callback, and argument in a tail queue. Suspend/powerdown callbacks run in registration order; resume callbacks run in reverse. Establish prints a deprecation warning.

Simple hook lists:
- `simplehook_create()` allocates a `khook_list_t`, initializes a mutex/CV/list, and starts in idle state.
- `simplehook_dohooks()` marks the list in use, records the active LWP and active hook, drops the list lock around each callback, skips hooks whose function has been nulled, broadcasts waiters for hooks removed while active, removes marked nodes after traversal, and returns `EBUSY` if another traversal is already running.
- `simplehook_establish()` inserts a hook under the list lock.
- `simplehook_disestablish()` removes idle hooks immediately; if hooks are running, it nulls the callback/argument, waits if another LWP is currently executing that hook, and lets `simplehook_dohooks()` free the node.
- `simplehook_has_hooks()` reports whether the list is nonempty.

Concurrency and integration:
- Global process hook families use rwlocks so registration/removal excludes callback traversal.
- Simple hook traversal explicitly supports disestablish racing with callbacks by marking callbacks null and using a CV.
- Root-spec hooks are serialized by the kernel configuration lock.

Risks and notes:
- `simplehook_dohooks()` is single-runner only; concurrent execution returns `EBUSY`.
- `simplehook_has_hooks()` only checks list emptiness, so it can report true for hooks that have been marked null but not yet removed during a traversal.
- Power hooks are deprecated but still maintained for compatibility.
