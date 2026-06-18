# sources/storage-engines/wiredtiger/test/salvage/salvage.c

Purpose: synthetic file-level salvage test for row-store and variable column-store pages. It builds controlled page fragments with chosen record ranges and write generations, runs WiredTiger salvage/verify/dump, and compares the dump to expected results.

Important APIs and control flow: `main()` parses `-r`, `-t var|row`, and `-v`, then runs `t()` for unique and non-unique values. `run()` contains 24 scenarios covering empty files, sequential pages, overlapping duplicate ranges, prefixes, suffixes, middle overlaps, and column-store missing ranges. `build()` creates a one-page `file:__slvg.load` with configured key/value formats and fixed page sizes. `copy()` appends the file description and modified page image to `__slvg.prep`, rewriting `WT_PAGE_HEADER.recno`, `write_gen`, and block checksum. `process()` copies prep to salvage file, runs `session->salvage`, `verify`, dumps through a `dump=print` cursor, and compares output with `__slvg.result`.

State and persistence behavior: recreates `WT_TEST` for every run and creates `__slvg.load`, `__slvg.prep`, `__slvg.slvg`, `__slvg.dump`, and `__slvg.result`. Logging is disabled because the test mutates WiredTiger files directly and must avoid recovery rewriting the synthetic state.

Dependencies and integration points: depends on internal page header/block structures, checksum helpers, `__wt_page_type_string`, endian swaps, and public salvage/verify/cursor APIs. The output comparison uses `cmp`.

Risks: highly coupled to WiredTiger on-disk page layout, block header checksum rules, and page size assumptions. Direct file manipulation can fail if layout or allocation behavior changes. Some scenarios are meaningful only for column store.

Test signals: for each scenario, salvage plus verify must succeed and `cmp __slvg.dump __slvg.result` must pass for both unique and non-unique values.
