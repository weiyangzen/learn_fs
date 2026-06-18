# File Research: sources/os/linux/linux/fs/seq_file.c

Generic kernel sequential-file framework used by procfs/debugfs-style synthetic files.

Core lifecycle APIs are `seq_open()`, `seq_read_iter()`, `seq_read()`, `seq_lseek()`, and `seq_release()`. The framework owns `struct seq_file`, serializes reads/seeks with `m->lock`, lazily allocates and grows the buffer, and drives caller-provided `seq_operations` callbacks.

Read traversal handles arbitrary `ki_pos` by replaying records via `traverse()`, supports `SEQ_SKIP`, detects buggy `.next()` implementations that do not advance position, and doubles the buffer on overflow until `MAX_RW_COUNT` prevents further growth.

Formatting helpers include `seq_printf()`, `seq_vprintf()`, `seq_escape_mem()`, pathname printers, decimal/hex fast paths, `seq_write()`, `seq_pad()`, and `seq_hex_dump()`. Single-record helpers include `single_open()`, `single_open_size()`, and `single_release()`.

Iterator helpers cover `list_head`, RCU lists, `hlist`, RCU hlists, and percpu hlists. `seq_file_init()` creates the global `seq_file` slab cache.
