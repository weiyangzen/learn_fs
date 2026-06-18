# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_modify_order.py

## Purpose

`ldap_modify_order.py` is a Samba DSDB regression/compatibility test for LDAP modify operation ordering. It proves that Samba's modify processing gives stable, expected results for every permutation of a set of add, replace, and delete operations in one `Message`, including cases where attribute applicability, syntax, single-valued constraints, object-class changes, and linked attributes interact.

Unlike typical unit tests, this file compares a generated signature against checked-in expected data files under `source4/dsdb/tests/python/testdata`. That makes the expected behavior explicit for every operation permutation.

## Important APIs, Types, and Functions

The central helper is `_test_modify_order(start_attrs, mod_attrs, extra_search_attrs=(), name=None)`. It creates a fresh object for each permutation of `mod_attrs`, applies the permuted LDB `Message`, searches the resulting object, clusters permutations by identical result or error, normalizes the base DN to `{base dn}`, and compares the signature with `testdata/<name>.expected`.

Other important functions and members:

- `_build_ldb_strerr()` builds a numeric LDB error-code-to-name table from the `ldb` module for stable signatures.
- `ModifyOrderTests.setUp()` creates an admin `SamDB` connection and stores the domain DN.
- `delete_object()` and `get_user_dn()` support cleanup and optional normal-user credential creation.
- `get_dsdb(creds=None)` opens `SamDB` with a system session and the selected credentials.
- Test cases such as `test_modify_order_mixed`, `test_modify_order_objectclass`, `test_modify_order_singlevalue`, `test_modify_order_inapplicable`, `test_modify_order_container_flags`, and `test_modify_order_member` define targeted start and modify tuples.

The script supports `--rewrite-ground-truth` to regenerate expected signatures, `--verbose` to print signatures, and `--normal-user` to run modify attempts with a newly created non-admin user instead of admin credentials.

## Control Flow

The file first builds `LDB_STRERR`, defines the test class, then parses options and normalizes the host into `tdb://` or `ldap://`. During each test, `_test_modify_order()` optionally creates a normal user and credentials, computes every permutation using `itertools.permutations`, creates one test object per permutation, applies the modification message, captures either the LDB error name/number or the sorted searched attribute values, and stores the operation ordering under that result cluster.

After all permutations run, it joins the signature text, substitutes the real base DN, optionally rewrites the expected file, reads the expected file, and calls `assertStringsEqual()`.

## State and Persistence Behavior

The test mutates a live DSDB by creating many `cn=ldaptest_<name>_<index>,cn=users,<base>` objects. Cleanup is registered with `addCleanup()` after each add. The `--normal-user` mode also creates `user123` with a fixed password and deletes it after the test. The ground-truth mode writes persistent `.expected` files in the source tree, but normal runs only read them.

The signature intentionally preserves operation order and result grouping, so it detects subtle ordering and module-processing changes even when the final object state is otherwise valid.

## Dependencies and Integration Points

The file depends on `SamDB`, `system_session`, LDB `Message`/`MessageElement`/`Dn`, modify flags, `LdbError`, Samba credential helpers, `delete_force`, subunit test running, and the `testdata` expected-output directory. It exercises DSDB modify internals for object-class validation, attribute syntax validation, single-valued enforcement, attribute applicability, integer parsing, linked attributes (`member`/`memberOf`), and access-control differences between admin and normal-user credentials.

## Risks and Edge Cases

Permutation coverage grows factorially with the number of modify tuples, so adding many operations to a case can make the test expensive and create many live objects. The expected files are compatibility contracts; `--rewrite-ground-truth` can accidentally bless a regression if used without review. Fixed normal-user credentials and object names can collide with concurrent runs or stale objects. Result signatures sort searched values, which is useful for set-like attributes but can hide ordering bugs for attributes where order is significant unless the operation/result text itself exposes them.

## Test Signals

Passing tests mean Samba applies complex multi-operation LDAP modifies consistently with the checked ground truth. The strongest signals are stable clustering across all permutations, correct LDB error names for invalid orderings, expected behavior when object-class changes make attributes newly applicable or inapplicable, correct handling of single-valued replacement/delete/add combinations, and linked-attribute consistency for `member` plus `memberOf`.
