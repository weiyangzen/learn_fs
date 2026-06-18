# sources/user-network-fs/samba/source4/dsdb/tests/python/subtree_rename.py

## Purpose

`subtree_rename.py` tests Samba AD behavior when an OU subtree is renamed while objects inside or outside the subtree are connected by linked attributes. It verifies that forward links, backlinks, and binary DN links are rewritten or preserved correctly after subtree moves and later deletes. It also includes a larger timing-oriented scenario that stresses rename performance after many links.

## Important APIs, Types, and Functions

`SubtreeRenameTests` opens `SamDB`, creates three OU DNs (`subtree1`, `subtree2`, `subtree3`), and provides helpers for object creation and linked-attribute mutation. `add_object()` and `add_objects()` create users, groups, and computers. `add_linked_attribute()`, `remove_linked_attribute()`, and `replace_linked_attribute()` build `ldb.Message` modifications over attributes like `member`. `add_binary_link()` constructs a binary DN value in `B:<hexlen>:<hexdata>:<dn>` form for `msDS-RevealedUsers`, and backlink checks inspect `msDS-RevealedDSAs`.

Assertion helpers `attr_search()`, `assert_links()`, `assert_forward_links()`, and `assert_back_links()` retrieve attributes with optional controls, normalize values to strings, sort, and compare expected link sets. `get_object_guid()` reads `objectGUID` and formats it through `misc.GUID`.

## Control Flow

Setup creates two source OUs and optionally deletes leftovers when `--delete-in-setup` is passed. Most tests create users, groups, and computers in different combinations across `ou1` and `ou2`, add normal group membership links plus binary revealed-user links, rename `ou1` to `ou3`, update expected DN strings with `.replace(self.ou1, self.ou3)`, delete one linked object, and assert final forward/backlink state.

The scenarios differ by which classes are moved: a whole tree, only groups, only users, non-computers while computers stay elsewhere, and a larger tree with 50 users, 10 groups, and 7 computers. The larger test records link and rename timings to stderr but does not assert elapsed time.

## State and Persistence Behavior

The suite mutates live directory state by creating OUs, users, groups, computers, normal links, and binary DN links. Teardown deletes all three test OUs with `tree_delete:1` unless `--no-cleanup` is used. Some tests delete moved objects after rename to ensure backlinks are cleaned. Because the DN replacement strategy assumes simple string substitution, object names are chosen so the OU suffix is the only relevant part replaced.

## Dependencies and Integration Points

The tests exercise Samba's subtree rename implementation, linked-attribute module, backlink maintenance, binary DN parsing and rewriting, `msDS-RevealedUsers`/`msDS-RevealedDSAs` semantics, LDB modify operations, and tree-delete behavior. They also integrate with debug coloring via `samba.colour` and use `binascii.hexlify` to construct binary DN prefixes.

## Risks and Edge Cases

Binary DN removal has a different formatting path than addition and appears less exercised by the current tests. The assertion helper permits duplicate backlink values, which matters because multiple binary links from one computer to one target can produce repeated backlinks. `assertRaisesLdbError(20, ...)` for duplicate binary link creation depends on the specific LDB error code. Cleanup can be intentionally disabled for debugging, leaving state that affects later runs. The big test is primarily a smoke/performance signal and lacks explicit post-rename correctness assertions.

## Test Signals

Pass signals include group `member` values following renamed DNs, `memberOf` backlinks reflecting surviving groups only, binary forward links rewritten to the new subtree DN, binary backlinks containing the expected source computers with duplicates where multiple binary values exist, deleted linked objects disappearing from backlinks, and large linked subtrees renaming without exceptions.
