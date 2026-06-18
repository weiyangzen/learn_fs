# sources/test-tools/kdevops/playbooks/python/workflows/fstests/xunit_merge_all.py

Purpose: Merges all xUnit XML files in a result tree into a single JUnit test suite.

Key APIs and flow: `get_test_suite()` loads a file with `JUnitXml.fromfile()` and requires the parsed object to be a `TestSuite`. `merge_ts()` appends test cases from one suite to another and updates statistics. `main()` walks the result directory, processes every `.xml`, initializes the aggregate from the first suite, merges the rest, and writes the output.

State, dependencies, integration: Reads XML files and writes the requested output file. Depends on `junitparser`. Used in fstests reporting when downstream consumers want one xUnit file.

Risks and test signals: It rejects `JUnitXml` containers even if they are valid JUnit XML; merge count excludes the first file; ordering follows `os.walk()` order; parse errors other than IOError are not handled. Tests should cover one file, multiple suites, container XML, malformed XML, no XML files, and statistics updates.
