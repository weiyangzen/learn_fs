# sources/user-network-fs/samba/source3/lib/file_id.c

Purpose: provides comparison, formatting, and compact serialization helpers for `struct file_id`.

Important APIs/types/functions: `file_id_equal()`, `file_id_str_buf()`, and `push_file_id_16()`.

Control flow: helpers directly compare fields, format into caller buffers, or write dev/inode into a 16-byte byte-order-safe buffer.

State/persistence behavior: no mutable state. The 16-byte serialization omits `extid`, so it is only suitable where dev/inode identity is enough.

Dependencies/integration: used by locking, open-file tracking, debug output, and torture diagnostics.

Risks/test signals: equality must include `extid`; serialization ordering must stay stable. Tests should cover extid differences and byte format stability.
