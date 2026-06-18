<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.py -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_test.py

Purpose: Python binding parity test for the C auparse harness, verifying that `auparse.AuParser` exposes equivalent source modes, cursor traversal, search, feed callbacks, timestamp objects, descriptor sources, and file-object sources.

Important APIs and functions: `walk_test`, `light_test`, `simple_search`, `compound_search`, and `feed_callback` mirror the C helper structure while using Python methods such as `parse_next_event`, `first_record`, `next_record`, `first_field`, `next_field`, `find_field`, `interpret_field`, `get_timestamp`, `search_add_item`, `search_add_regex`, `search_set_stop`, `search_next_event`, `feed`, and `flush_feed`. `none_to_null` normalizes Python `None` display.

Control flow and state: the script executes thirteen named tests. Early tests use buffer and file sources; middle tests exercise search rules and regex; feed tests chunk buffers and files; later tests open a descriptor and a Python file object to ensure wrapper ownership and duplicate descriptor behavior are correct. Output is deterministic and diffed against `auparse_test.ref.py`.

Dependencies and integration: imports the locally built `auparse` module, uses `srcdir` for fixture lookup, and is launched by `run_auparse_tests.sh.in` with `PYTHONPATH`, `LD_LIBRARY_PATH`, and bytecode suppression.

Risks and test signals: reference output is sensitive to binding method names, exception behavior, path normalization, and C library output. Descriptor/file-pointer tests specifically signal ownership regressions by checking the original fd/file remains readable after parser destruction.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.py -->
