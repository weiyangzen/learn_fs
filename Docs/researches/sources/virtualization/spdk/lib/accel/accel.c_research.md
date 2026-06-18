# File Research: sources/virtualization/spdk/lib/accel/accel.c

`accel.c` is the core SPDK accelerator framework implementation. It owns global module registration and opcode assignment, per-channel task/sequence/buffer pools, sequence execution, memory-domain bounce-buffer handling, crypto-key lifecycle, framework initialization/finalization, config JSON dumping, driver selection, options, and stats.

Major public submission APIs build `spdk_accel_task` objects for copy, dualcast, compare, fill, CRC32C, copy+CRC32C, compress/decompress, encrypt/decrypt, XOR, DIF, and DIX operations. Single-shot submissions allocate a task from the channel pool, populate source/destination iovecs, opcode-specific fields, domains, and completion callback, then dispatch through the selected module for that opcode.

The sequence API lets callers append operations to a `spdk_accel_sequence`. Appended operations carry memory-domain metadata, optional per-step callbacks, and are later executed by `spdk_accel_sequence_finish()`. Before execution, the framework attempts copy-elision/merge optimizations so adjacent copy operations can be folded into neighboring operations when iovec and domain relationships allow it.

The sequence state machine is a central design point. It moves through virtual accel-buffer allocation, bounce-buffer allocation, memory-domain pull/push operations, module task execution, driver execution, per-task completion, error handling, and final sequence completion. It prevents recursive processing with `in_process_sequence`, and completion paths re-enter the state machine only after state changes.

Memory-domain support is handled in two layers. The accel framework exposes its own accel memory domain where buffers are represented by a sentinel pointer plus an `accel_buffer` domain context. It also adapts operations for modules that do not support foreign memory domains by allocating iobuf-backed bounce buffers, pulling source data into them, and pushing destination data back after task completion.

The crypto-key path validates key creation parameters, cipher strings, tweak-mode strings, module crypto support, AES-XTS second-key requirements, key-size equality, and identical XTS keys with timing-side-channel-aware comparison. Key material is scrubbed before free, key objects are kept in a spinlock-protected keyring, and module-specific key init/deinit hooks own hardware/software private state.

Initialization registers the accel io_device, creates the accel memory domain, initializes modules, optionally initializes an accel driver, assigns opcodes by module priority plus user overrides, validates paired encrypt/decrypt and compress/decompress module choices, initializes opcode memory-domain support flags, and registers the iobuf module. Finalization unregisters the io_device, destroys crypto keys, frees opcode overrides, finishes modules, destroys spinlocks, and destroys the memory domain.

Stats are tracked per channel and folded into global stats when channels are destroyed. `accel_get_stats()` aggregates global retired-channel stats plus all live channel stats asynchronously. Opcode-specific counters track executed, failed, and byte counts; retry counters cover task, sequence, iobuf, and buffer-descriptor pressure.

Important dependencies include `spdk/accel_module.h`, `spdk/thread.h`, `spdk/dma.h`, `spdk/iobuf`, memory domains, JSON config writers, `spdk/hexlify.h`, and SPDK spinlocks. The file assumes all opcodes ultimately have a module, with the software module providing fallback coverage.

Research notes: resource sizing is governed by `spdk_accel_opts`, and `task_count` must stay at or above the in-sequence deadlock-avoidance limit. The framework uses assertions for several internal invariants, especially aux-data pool availability and state transitions, so integration mistakes tend to fail hard in debug builds.
