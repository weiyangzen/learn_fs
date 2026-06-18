# sources/test-tools/lcov/scripts/history.pm

Purpose: load-balancing history callback for lcov/geninfo/genhtml. It reads prior `--profile` JSON files and predicts per-file execution time so parallel schedulers can start historically expensive work first.

Important APIs: package `history` exports `new`; callback method `history($name)` returns a predicted time or undef. Helper `appendElements($predicted, $in, $sub)` accumulates totals and counts for averaging.

Control flow and state: construction inspects `lcovutil::tool_name` to decide required profile keys (`file` for genhtml, `file` and `find` for geninfo/lcov capture), expands glob arguments, loads JSON through `JsonSupport::load`, validates required keys, and ignores invalid/empty inputs via `lcovutil::ignorable_error`. With multiple profiles, it averages values. For geninfo, it strips capture-directory prefixes using directories from the `find` profile key before merging file costs.

Dependencies and integration: depends on `lcovutil`, `Time::HiRes`, and profile data schemas emitted by lcov tools. It stores callback processing time in `%lcovutil::profileData`.

Risks and test signals: profile schema drift or tool-name mismatch causes ignored history. Regex construction from directory names is not escaped. Multiple data files are averaged equally regardless of recency. Test signals include profile generation, `--history-script` scheduling tests, invalid JSON handling, and lcov/geninfo/genhtml-specific key validation.
