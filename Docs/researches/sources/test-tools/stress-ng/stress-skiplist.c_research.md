# sources/test-tools/stress-ng/stress-skiplist.c

Purpose: implements the `skiplist` stressor, building a probabilistic skip list of 32-bit values and verifying all inserted values can be found.

Important APIs/types/functions: `skip_node_t`, `skip_list_t`, `skip_list_random_level`, `skip_node_alloc`, `skip_list_init`, `skip_list_insert`, `skip_list_search`, `skip_list_ln2`, `skip_list_free`, and `stress_skiplist`.

Control flow: the worker resolves `skiplist-size`, computes maximum level as log2(size), synchronizes start, then each iteration initializes a list, inserts `n` Gray-code-like values `(i >> 1) ^ i`, searches for all of them, frees the list, and increments bogo ops. Allocation failures return no-resource, and missing search hits are hard failures.

State and persistence behavior: all state is heap allocated per iteration. The head node is circular at each level, nodes allocate their forward-pointer arrays adjacent to the node object, and `skip_list_free` walks level 1 to release all nodes.

Dependencies and integration points: registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, always verify, with `skiplist-size` option. It depends on stress-ng random generation for levels and global minimize/maximize flags.

Risks and test signals: risks include allocation pressure, off-by-one level handling, duplicate-value behavior, and `size_t` underflow in reverse level loops if invariants are broken. Test signals are successful search of every inserted value and complete freeing without leaks.
