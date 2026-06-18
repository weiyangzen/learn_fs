# File Research: sources/os/bsd/openbsd-src/sys/sys/siginfo.h

`siginfo_t` layout and signal-code namespace.

This header defines `union sigval`, user/kernel signal-origin tests, generic `SI_*` codes, architecture-related signal cause codes for `SIGILL`, `SIGFPE`, `SIGSEGV`, and `SIGBUS`, plus trap and child-status codes. Unsupported `SIGPOLL` and `SIGPROF` layouts remain disabled in `#if 0`, but accessor macros still name those union members for compatibility with historical shape.

The public `siginfo_t` is fixed at `SI_MAXSZ` 128 bytes and stores signal number, code, errno, and a padded union for process, child, and fault data. Kernel builds expose `initsiginfo()`.

Filesystem/storage relevance: indirect. Filesystem syscalls can be interrupted or can trigger signal delivery paths, and `SIGXFSZ` is named in the disabled file-info block, but this header mainly defines process-signal ABI rather than VFS behavior.
