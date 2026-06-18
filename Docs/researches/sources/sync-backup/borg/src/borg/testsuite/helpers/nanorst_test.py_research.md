# sources/sync-backup/borg/src/borg/testsuite/helpers/nanorst_test.py

Purpose: tests Borg's minimal reStructuredText-to-text converter.

Important APIs and control flow: cases cover inline emphasis/literal markup stripping, multi-line inline spans, inline escaped asterisks, comments with and without blank-line directive context, `.. note::` directive rendering, reference substitution with a provided map, undefined-reference errors, and code-block text at end of string.

State and persistence: pure string transformation; no persistent state.

Dependencies and integration points: depends on `helpers.nanorst.rst_to_text`. It supports help/doc text rendering in contexts where full docutils is unnecessary.

Risks: parser intentionally handles a tiny rst subset. Ambiguous comment/directive layout and undefined references are the main behavioral edges.

Test signals: exact rendered strings and `ValueError` for missing references.
