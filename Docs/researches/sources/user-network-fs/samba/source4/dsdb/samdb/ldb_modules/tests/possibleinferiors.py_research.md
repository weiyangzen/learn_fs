# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/possibleinferiors.py

Purpose: `possibleinferiors.py` is a Samba test script that validates the generated `possibleInferiors` schema attribute against an independently constructed implementation of the AD algorithm.

Important APIs, types, and functions: The script parses a database or LDAP URL and optional class name, opens `samba.Ldb`, discovers `schemaNamingContext` from rootDSE, and compares `possible_inferiors_search()` with `possible_inferiors_constructed()`. Helper functions `supclasses()`, `auxclasses()`, `subclasses()`, and `posssuperiors()` build cached class relationships. `pull_classinfo()` reads all classSchema objects and prepares subclass maps. `test_class()` performs the assertion and exits nonzero on mismatch.

Control flow: After argument parsing and credential setup, the script connects to local LDB or remote LDAP, switching to paged searches for LDAP URLs. It reads rootDSE, loads class metadata from the schema partition, precomputes subclasses, then tests either all classes or the requested class. For each tested class, it searches the live generated `possibleInferiors`, constructs the expected sorted unique list by walking possible superiors and subclasses, and prints a detailed diff before exiting on failure.

State and persistence behavior: The script is read-only. Runtime state is an in-memory dictionary keyed by `ldapDisplayName`, with memoized lists for superclasses, auxiliary classes, possible superiors, and subclasses. It does not modify the database or write artifacts.

Dependencies and integration points: It depends on Samba Python bindings, `ldb`, Samba option/credential helpers, and the `schema_data` module's generated `possibleInferiors` behavior. The `--wspp` flag switches to a variant based on WSPP documentation, while default behavior follows observed Windows Server 2003/2008 behavior noted in comments.

Risks: The script shadows Python built-in names such as `list` and `set`, which is stylistically risky but localized. Recursive relationship expansion assumes schema class references are present in `classinfo`; malformed schemas could raise key errors. Because comparison is sorted unique strings, it validates membership but not original ordering or duplicate behavior. Remote LDAP results depend on credentials and server-side module stack configuration.

Test signals: Successful completion prints `Lists match OK`. Failures print both returned and constructed lists plus aligned differences for the tested class. This is a direct regression signal for `schema_data.c` `generate_possibleInferiors()` and related schema relationship generation.
