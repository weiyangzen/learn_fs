# sources/security-integrity/selinux/libsemanage/src/compressed_file.h

Purpose: declares the internal possibly-compressed file abstraction used for module and CIL payload handling.

Important APIs/types/functions: `struct file_contents` contains uncompressed `data`, `len`, and a `compressed` discriminator. Declares `map_compressed_file`, `unmap_compressed_file`, and `write_compressed_file`.

Control flow: callers map a path, use the returned uncompressed memory, and always release with `unmap_compressed_file`. Writers pass raw bytes and let the implementation apply configured compression.

State and persistence behavior: the struct describes transient mapped or allocated memory. `write_compressed_file` is the only persistent operation and writes to the provided path using handle configuration.

Dependencies and integration points: includes `sys/mman.h`, `sys/types.h`, and internal `handle.h`; consumed by `direct_api.c` module install/extract paths.

Risks: callers must not mix ordinary `free`/`munmap` with this abstraction. Test signals are clean map/unmap for both compressed and uncompressed files and writer output readable by `map_compressed_file`.
