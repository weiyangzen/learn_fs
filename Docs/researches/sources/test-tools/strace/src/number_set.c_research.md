<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/number_set.c -->
# sources/test-tools/strace/src/number_set.c

Purpose: implements dynamic bitset arrays used for syscall, signal, status, fd, pid, quiet, and injection qualifiers.

Important APIs/types/functions: opaque `struct number_set`, `is_number_in_set`, `is_number_in_set_array`, `add_number_to_set`, `clear_number_set_array`, `invert_number_set_array`, `is_complete_set`, `alloc_number_set_array`, and `free_number_set_array`.

Control flow: bit operations map numbers to 32-bit slots; insertion grows the slot vector; membership XORs the stored bit with the set-level inversion flag; completeness counts set bits or recognizes an inverted empty set as universal.

State and persistence behavior: number sets are heap-allocated mutable process state owned by qualifier parsing and global decoder configuration.

Dependencies and integration points: used by filtering, path tracing, fd decoding, PID decoding, injection, and quiet-option logic; depends on `xmalloc`, `static_assert`, and `popcount32`.

Risks: inverted semantics are easy to misuse. Completeness depends on caller-provided max counts. The implementation assumes `number_slot_t` is 32-bit.

Test signals: empty sets, add and membership, array index behavior, inversion, clear, complete sets, high-number growth, and allocation/free under sanitizer builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/number_set.c -->
