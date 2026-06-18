# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isdata.h

Defines the core data structure for expandable interpreter ref stacks. It documents the GC cleanliness requirements for stack blocks: unused areas must contain valid refs, often nulls, so the collector can scan blocks safely without following stale pointers.

Defines `s_ptr`, `const_s_ptr`, opaque `gs_ref_memory_t`, `ref_stack_t`, and `ref_stack_params_t`. `ref_stack_s` contains the dynamic top pointer, current block boundaries, current block ref, extension accounting, maximum stack ref, failing request size, stack margin, body size, immutable params, and allocator pointer.

Also declares the GC structure macro `public_st_ref_stack`, with two GC-visible pointers: `current` and `params`.
