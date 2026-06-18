# File Research: sources/os/linux/linux/fs/char_dev.c

Core Linux character device registration and dispatch implementation.

Major responsibilities:
- Maintains registered char device number ranges in `chrdevs[]`, protected by `chrdevs_lock`.
- Allocates static or dynamic major numbers.
- Registers/unregisters char device regions.
- Provides `__register_chrdev()` and `__unregister_chrdev()` convenience APIs that combine region reservation with `struct cdev` lifecycle.
- Maps device numbers to `struct cdev` through global `cdev_map`.
- Handles first open of character special files by replacing default fops with the registered cdev’s fops.
- Exports cdev APIs to modules.

Important functions:
- `find_dynamic_major()`: searches normal and extended dynamic major ranges.
- `__register_chrdev_region()`: validates major/minor range, checks overlap in sorted hash bucket, and inserts region.
- `register_chrdev_region()` / `alloc_chrdev_region()`: public region allocation APIs.
- `__register_chrdev()`: reserves region, allocates cdev, sets owner/ops/name, calls `cdev_add()`.
- `unregister_chrdev_region()` / `__unregister_chrdev()`: remove range and optional cdev.
- `chrdev_open()`: resolves inode `i_rdev` to cdev, pins module/kobject, installs fops, calls driver open.
- `cdev_add()`, `cdev_del()`, `cdev_alloc()`, `cdev_init()`, `cdev_set_parent()`.
- `cdev_device_add()` / `cdev_device_del()`: paired cdev/device registration helpers.
- `chrdev_init()`: initializes `cdev_map` with module autoload probe.

Concurrency/lifetime:
- `chrdevs_lock` protects major/minor range registry and module autoload map initialization.
- `cdev_lock` protects inode-to-cdev links and cdev inode lists.
- `cdev_get()` pins both owner module and kobject.
- `cdev_purge()` clears `i_cdev` links on cdev release.
- Opened cdev fops can remain callable after `cdev_del()`; comments explicitly warn callers.

Exports:
- Region APIs, cdev init/alloc/add/del/parent/device helpers, and legacy register/unregister helpers are exported.
