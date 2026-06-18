# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact.h

Defines the central exec image-activation structures used by `execve` handling. `struct image_args` tracks copied argument/environment strings, executable filename, fd, buffer state, and counts. `MAXSHELLCMDLEN` is one page.

`struct image_params` is the kernel execution context passed to image activators. It includes process/thread, vnode/object/attributes, file header, entry and relocation addresses, interpreter details, ELF auxargs, first page mapping, argv/envv output pointers, sysent vector, stack properties, credential transition state, ASLR flag state, interpreter vnode, and bookkeeping booleans.

Kernel declarations cover argument allocation/copying, permission checks, stack mapping, VM-space replacement, register setup, shell image activation, and pre/post exec hooks.
