# File Research: sources/os/linux/linux-stable/fs/char_dev.c

## Purpose
Implements Linux character-device major/minor registration, dynamic major allocation, cdev lifetime management, dev_t-to-cdev lookup, and default character special file open dispatch.

## Main Interfaces
- Region registration: `register_chrdev_region()`, `alloc_chrdev_region()`, `unregister_chrdev_region()`.
- Legacy combined registration: `__register_chrdev()`, `__unregister_chrdev()`.
- cdev lifecycle: `cdev_alloc()`, `cdev_init()`, `cdev_add()`, `cdev_del()`, `cdev_put()`.
- cdev/device helpers: `cdev_set_parent()`, `cdev_device_add()`, `cdev_device_del()`.
- Open dispatch: `def_chr_fops`, internal `chrdev_open()`.
- Initialization/proc: `chrdev_init()`, `chrdev_show()` under procfs.

## Control Flow
Major/minor reservations are tracked in a hash table of `char_device_struct` ranges protected by `chrdevs_lock`. `__register_chrdev_region()` validates major and minor bounds, finds a dynamic major if requested, checks for overlapping reserved ranges, and inserts the new range in sorted order. Multi-major public APIs split large `dev_t` ranges at major boundaries and roll back partial registration on failure.

`cdev_add()` maps a `dev_t` range into `cdev_map` with exact match/lock callbacks and takes a parent kobject reference. Opening a character special file starts at `def_chr_fops.open`; `chrdev_open()` resolves `inode->i_rdev` through `cdev_map`, attaches the resolved cdev to the inode, takes module/kobject refs, replaces the file operations with the device’s real fops, and calls the device open method.

Removal unmaps the cdev range and drops kobject refs. Release handlers purge inode back-pointers from the cdev list before freeing dynamic cdev storage or releasing parent refs.

## State And Synchronization
`chrdevs_lock` protects reservation tables and module autoload map initialization. `cdev_lock` protects inode-to-cdev attachment and cdev inode lists. `cdev_get()` combines `try_module_get()` with `kobject_get_unless_zero()` to prevent opens racing with removal.

## Integration Points
Exports the standard cdev API for drivers and backs VFS open of character device inodes. It also integrates with sysfs device lifetimes through `cdev_device_add()` and `cdev_set_parent()`.

## Risks And Review Focus
- Open/remove races depend on correct module and kobject reference ordering.
- Region overlap checks must remain exact across major boundaries and dynamic major allocation.
- `cdev_device_add()` notes that userspace may open the cdev even if later `device_add()` fails.
