# File Research: sources/os/linux/linux-stable/fs/verity/init.c

Initializes fs-verity global state and logging. `fsverity_msg()` is a rate-limited printk helper that includes filesystem id and inode number when available. The init path runs as a `late_initcall`, checking hash algorithm metadata, initializing the `fsverity_info` cache/rhashtable, creating the read verification workqueue, registering sysctl controls, initializing optional signature support, and registering optional BPF kfuncs.

When builtin signatures are configured, the sysctl table exposes `/proc/sys/fs/verity/require_signatures`, constrained to 0/1. Without sysctl support, initialization stubs out sysctl registration.
