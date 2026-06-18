# sources/test-tools/fio/engines/e4defrag.c

Purpose: Implements an `e4defrag` engine that simulates ext4 defragmentation by issuing `EXT4_IOC_MOVE_EXT` ioctls from a donor file to the target file.

Important APIs/functions: Registers engine callbacks for init, queue, generic file open/close/size, and cleanup. Options are `donorname` and `inplace`. Internal state `e4defrag_data` stores donor fd and block size.

Control flow: Init requires a donor name, prefixes it with job directory if present, opens/creates the donor, optionally preallocates donor space for the workload range, stats it to learn block size, and stores state. Queue accepts only write directions, optionally fallocates donor space for the IO range in inplace mode, fills `struct move_extent` with donor fd and block ranges derived from offset/length, calls `ioctl(EXT4_IOC_MOVE_EXT)`, maps moved length to fio residual/error, and truncates donor back to zero in inplace mode. Cleanup closes donor and frees state.

State/persistence: Donor file persists on disk unless external cleanup removes it. Engine state is per-thread.

Dependencies/integration: Depends on ext4 move-extent ioctl, fallocate/ftruncate, fio read-only checks, and generic file callbacks.

Risks: Only meaningful on ext4 with compatible files. Donor path construction uses `sprintf` into `PATH_MAX`. Inplace truncate errors can override earlier success. The engine treats defrag as write-only even though data content should be unchanged.

Test signals: Tests need ext4 support, donor required validation, preallocated and inplace modes, partial moved lengths near EOF, and read-only mode rejection.
