# File Research: sources/os/bsd/dragonflybsd/sys/sys/imgact.h

`imgact.h` defines exec image-activation state. It includes mount and lwbuf definitions and sets `MAXSHELLCMDLEN` to 128.

`struct image_args` tracks the argument/environment string buffer, argv/env starts, end pointer, executable filename, remaining space, and argument/environment counts. `struct image_params` tracks the executing process, args, executable vnode and attributes, mapped image header, entry address, flags for resident/vmspace/interpreted state, interpreter name, ELF auxargs, first-page mapping cache, BSD/OS `ps_strings`, and exec path storage.

Kernel prototypes cover resident image activation, permission checks, new vmspace setup, and shell-script image activation.
