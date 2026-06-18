# File Research: sources/os/bsd/dragonflybsd/sys/sys/kcore.h

Declares `kcore_make_file()`, which fills a `kinfo_file` record from a kernel `file` object, process id, uid, and descriptor number. It bridges kernel file structures to exported kernel-core/introspection data.

Relevant to filesystem research because it exposes open-file metadata for core/kernel inspection paths.
