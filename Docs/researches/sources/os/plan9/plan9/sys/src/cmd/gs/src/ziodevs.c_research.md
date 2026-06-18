# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevs.c

Direct stdio-backed `%stdin%`, `%stdout%`, and `%stderr%` IODevice implementation for the PostScript interpreter. It defines special IODevice descriptors using the `Special` dtype.

`stdin_init` marks stdin interactive in the library context. `stdin_open` allocates a file stream over `gs_stdin`, installs a custom process function that reads through `gp_stdin_read`, and returns a cached `ref_stdin` file object. The custom read process reads one character at a time in interactive mode but still uses a larger buffer for filters that need progress.

`stdout_open` and `stderr_open` allocate write streams over `gs_stdout` and `gs_stderr`, each with 128-byte buffers, cached file refs, and close behavior that flushes/closes the underlying file stream. `zget_stdin`, `zget_stdout`, and `zget_stderr` reopen cached standard streams through the IODevice table when necessary; `zis_stdin` recognizes this implementation by its custom process function.
