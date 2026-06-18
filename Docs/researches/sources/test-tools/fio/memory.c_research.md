# sources/test-tools/fio/memory.c

Purpose: implements IO buffer memory allocation, freeing, and optional memory pinning for fio jobs.

Important APIs/functions: `fio_pin_memory`, `fio_unpin_memory`, `allocate_io_mem`, and `free_io_mem`. Static helpers allocate/free memory via SysV shared memory, anonymous/file mmap, malloc, CUDA device memory, and hugepage variants.

Control flow: pinning maps anonymous memory and `mlock`s up to requested `lockmem`, clamping against physical memory with 128 MiB reserve. IO allocation computes total buffer size including direct-IO/page/mem alignment overhead, respects IO-engine custom allocators unless user options conflict, then dispatches by `mem_type`. Free mirrors the selected allocation path, closing/unlinking mmap files when appropriate and destroying CUDA resources.

State/persistence: mutates `thread_data` fields such as `pinned_mem`, `orig_buffer`, `orig_buffer_size`, `shm_id`, `mmapfd`, mmap keep flags, CUDA context/device pointers, and option-owned `mmapfile`. Shared memory and mmap files are OS resources that must be cleaned up.

Dependencies/integration: relies on fio options, IO engine flags/hooks, OS memory macros, hugepage config, CUDA config, logging, and error recording.

Risks/test signals: resource cleanup is complex on partial failure, especially shm attach failure, mmap open/truncate failure, and CUDA context allocation. `free_mem_mmap` uses `td->orig_buffer_size` in `munmap` despite receiving `total_mem`, so alignment-overhead accounting should be scrutinized. Tests should cover each memory mode, hugepage failures, engine allocator conflict, and mmapfile keep/unlink behavior.
