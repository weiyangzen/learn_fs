# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/joshua.py

Purpose: reads Joshua ensemble results and prints compact reproduce/error summaries in the current TestHarness2 output format.

Important APIs/types: SAX `ToSummaryTree`, helper `_print_summary`, and public `print_errors(ensemble_id)`.

Control flow: opens Joshua model, tails ensemble results, parses each XML result line into `SummaryTree`, derives a reproduce command (`bin/fdbserver -r ... -f ... -s ... -b ... --crash --trace_format ...`), filters warnings/errors/buggify sections, and prints XML or JSON according to config.

State and persistence: no writes. Maintains per-call command de-duplication to avoid duplicate JSON/XML keys.

Dependencies and integration: external `joshua.joshua_model`, XML SAX, config, and `test_harness.run.is_no_sim`. Invoked by `results.py`.

Risks and test signals: assumes Joshua record tuple shapes and XML lines; `errors.name == "ValgrindError"` check likely does not detect valgrind because `errors.name` is fixed. Test with multiple result tuple formats, duplicate commands, details mode, and missing attributes.
