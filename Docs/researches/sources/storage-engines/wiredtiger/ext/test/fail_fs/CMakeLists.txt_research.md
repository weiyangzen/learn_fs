# sources/storage-engines/wiredtiger/ext/test/fail_fs/CMakeLists.txt

This CMake file builds the fail filesystem test extension as `wiredtiger_fail_fs`. It declares `fail_fs.c` as the only source, creates a `MODULE` library, adds WiredTiger source/generated/config and test utility include directories, applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`, and links `test_util`.

The file has no runtime state; its persistent effect is a loadable module artifact used by tests. It depends on generated headers, core WiredTiger headers, and `test_util`. The main risk is build-configuration drift: this path always builds a module, so configurations without module loading need handling elsewhere. Build validation should confirm the target configures, compiles, links, and can be loaded by tests.
