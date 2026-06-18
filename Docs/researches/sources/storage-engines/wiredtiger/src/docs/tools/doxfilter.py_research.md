# sources/storage-engines/wiredtiger/src/docs/tools/doxfilter.py

## Purpose
Input filter for WiredTiger reference documentation. It rewrites documentation comments and expands custom `@arch_page` markers with structured architecture-page metadata from `dist/docs_data.py`.

## Important APIs and control flow
The script imports `docs_data.arch_doc_pages` into `arch_doc_lookup`. `process` converts `/*!` to `/**`, then calls `process_arch` if `@arch_page` appears. `process_arch` validates syntax, extracts page identifier and title, looks up data structures and files, and emits `@arch_page_top`, optional `@arch_page_table`, and `@arch_page_caution` directives. `err` reports filename and line context, although the visible code does not increment `linenum`. Main reads the first filename argument, prints processed content, and exits after one file.

## State, dependencies, integration, risks
State is transient lookup dictionaries and current filename/line globals. It depends on repository layout to locate `dist/docs_data.py`, Python, regular expressions, and Doxygen macros that understand the emitted commands. Risks include KeyError for unknown architecture page IDs, incomplete line-number reporting, processing only the first argument, and custom macro drift. Test signals are C docs with plain comments, valid and invalid `@arch_page` markers, pages with and without table data, and missing docs_data entries.
