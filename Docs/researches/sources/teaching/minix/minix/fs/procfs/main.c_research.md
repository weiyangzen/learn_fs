# File Research: sources/teaching/minix/minix/fs/procfs/main.c

`main.c` wires ProcFS into VTreeFS. It defines hook callbacks for initialization, lookup, getdents, read, and readlink, then passes them to `run_vtreefs`.

The private `construct_tree` helper recursively creates the static tree from `struct file` arrays, using `add_inode` and storing each file's data pointer as VTreeFS callback data. Directories recurse into child `struct file` arrays.

`init_hook` runs once. It initializes dynamic process-tree state with `init_tree`, creates static root files from `root_files`, initializes the service directory through `service_init`, and then suppresses duplicate initialization on restarts through a static flag.

`main` defines root directory metadata (`DIR_ALL_MODE`, root ownership, no device) and starts VTreeFS with the hook table, inode budget, root stats, expected dynamic root entries, and ProcFS buffer size.
