# sources/test-tools/syzkaller/executor/_include/flatbuffers/vector_downward.h

Purpose: This FlatBuffers builder support class implements a byte vector that grows from high addresses toward low addresses, matching FlatBuffers backward serialization. It also reserves the low-address side as a scratch area so temporary builder state can share the same allocation.

Important APIs and types: `vector_downward<SizeT>` owns or borrows an `Allocator` and exposes `reset`, `clear`, `clear_scratch`, `clear_allocator`, `clear_buffer`, `release_raw`, `release`, `ensure_space`, `make_space`, `get_custom_allocator`, `offset`, `size`, `unused_buffer_size`, `scratch_size`, `capacity`, `data`, `scratch_data`, `scratch_end`, `data_at`, `push`, `push_small`, `scratch_push_small`, `fill`, `fill_big`, `pop`, `scratch_pop`, `swap`, and `swap_allocator`.

Control flow and state: The object tracks `buf_`, `cur_`, `scratch_`, `reserved_`, `size_`, `initial_size_`, `max_size_`, `buffer_minalign_`, and allocator ownership. Writes to the serialized buffer call `make_space`, which ensures capacity, decrements `cur_`, and increments `size_`. Scratch writes grow upward from `buf_`. If unused space cannot satisfy a request, `reallocate` grows by max(request, half old capacity or initial size), rounds to minimum alignment, and calls `ReallocateDownward` to preserve both downward data and scratch contents.

Dependencies and integration points: It depends on `flatbuffers/base.h`, `default_allocator.h`, `detached_buffer.h`, allocator helpers, and `FLATBUFFERS_MAX_BUFFER_SIZE`. It is used by FlatBuffer builders to assemble final buffers and hand them off as `DetachedBuffer`.

Risks and test signals: Critical invariants are `buf_ <= scratch_ <= cur_ <= buf_ + reserved_`, maximum-size enforcement, ownership transfer in `release`, and preserving scratch/data during reallocation. Tests should cover empty release, move construction/assignment, custom allocator ownership, large growth, scratch collision, alignment rounding, and `pop`/`scratch_pop` balance.
