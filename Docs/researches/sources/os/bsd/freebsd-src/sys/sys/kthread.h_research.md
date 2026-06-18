# File Research: sources/os/bsd/freebsd-src/sys/sys/kthread.h

Defines descriptors and APIs for kernel processes and kernel threads. `struct kproc_desc` and `struct kthread_desc` provide linker/SYSINIT-friendly daemon startup metadata: name, main function, and optional global proc/thread pointer storage.

APIs create, exit, resume, suspend, shutdown, and start kernel processes and threads. `kproc_kthread_add()` creates a thread in a process, creating the process if necessary; `kthread_add()` creates a thread in an existing process.
