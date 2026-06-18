## sources/security-integrity/audit-userspace/src/ausearch-report.c

Purpose: formats matched `ausearch` events as raw, default, interpreted, CSV, or normalized text output.

Important APIs/functions: `output_event()` dispatches by `report_format`; `ausearch_load_interpretations()` and `ausearch_free_interpretations()` manage enriched interpretation state; `output_raw()`, `output_default()`, and `output_interpreted()` render record-oriented formats; `report_interpret()` interprets individual fields; `feed_auparse()` feeds complete events to auparse callbacks; `csv_event()` and `text_event()` produce normalized one-line outputs; `output_auparse_finish()` destroys feed parser state.

Control flow: default/interpreted modes output records in reverse item order except daemon messages. Interpreted mode rewrites type names, human time, field names/values, syscall context, and keys. CSV/text modes use `AUSOURCE_FEED`, set escape and EOE timeout, feed each record with restored separators/newlines, then flush to trigger callbacks.

State/persistence: static auparse parser for interpretations, static feed parser, loaded flag, syscall/machine/a0/a1 state, and CSV header flag. No persistence.

Dependencies/integration: depends on `ausearch-options`, `ausearch-parse`, `ausearch-lookup`, `auparse`, `auparse-idata`, normalization internals, and `lol_get_eoe_timeout()`.

Risks/test signals: functions temporarily mutate record messages to restore enriched separators/newlines and must restore them correctly. CSV output is not visibly quoting fields here, so comma/newline-containing interpretations need tests. Static parser state means multiple independent output streams are not isolated. Tests should cover all formats, enriched and raw events, key separator expansion, TTY data, normalized CSV extra flags, text normalization failures, and cleanup via `output_auparse_finish()`.
