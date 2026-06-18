# sources/user-network-fs/samba/source3/lib/file_id.h

Purpose: declares file-id helper functions and the printable buffer type.

Important APIs/types/functions: `struct file_id_buf`, `file_id_equal()`, `file_id_str_buf()`, and `push_file_id_16()`.

Control flow: no runtime flow; it defines the caller contract for comparing, logging, and serializing file ids.

State/persistence behavior: formatting is caller-buffer based; compact serialization is available through the implementation.

Dependencies/integration: included by source3 locking, VFS, and tests.

Risks/test signals: callers must provide valid buffers and understand the compact format. Compile and lock/open-file tests validate the API.
