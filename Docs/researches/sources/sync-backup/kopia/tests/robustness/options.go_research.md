<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/options.go -->
# sources/sync-backup/kopia/tests/robustness/options.go

This file provides `GetOptAsIntOrDefault`, a small helper for parsing integer option maps used by engine actions and file writers. It returns the default for nil maps, missing keys, or parse failures.

Control flow is intentionally forgiving: callers do not receive parse errors, so invalid option values silently fall back to defaults. The helper is heavily integrated with `fiofilewriter` and robustness test option construction.

There is no state or persistence. Risk is hidden configuration mistakes, especially in randomized tests where default values can make an intended bounded action much larger. Test signals are indirect through option-driven robustness tests; no dedicated unit test is present in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/options.go -->
