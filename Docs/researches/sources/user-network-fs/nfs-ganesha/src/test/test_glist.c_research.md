# sources/user-network-fs/nfs-ganesha/src/test/test_glist.c

Purpose: manual smoke test for `gsh_list` intrusive list operations.

Important APIs, types, and functions: defines `struct myteststruct` with embedded `glist_head`. Uses `glist_init`, `glist_add`, `glist_add_tail`, `glist_del`, `glist_add_list_tail`, `glist_splice_tail`, `glist_for_each`, and `glist_entry`.

Control flow: `basic_test` adds nodes to a list, appends a tail node, deletes one, combines another list, and prints contents. `splice_tail_test` builds two 5-node lists, splices the second onto the first, and prints both. `main` runs both tests.

State and persistence: only stack-allocated nodes and two global list heads.

Dependencies and integration points: built as `test_glist` and linked with `ganesha_nfsd` and thread libraries.

Risks: there are no assertions or nonzero exits on wrong behavior; it is output-inspection based. Stack node lifetime is safe within each function but would be unsafe if retained beyond the function.

Test signals: useful for visual debugging of list order and splice behavior, not a strong automated regression test.
