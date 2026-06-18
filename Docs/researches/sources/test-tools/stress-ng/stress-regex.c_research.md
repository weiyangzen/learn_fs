# sources/test-tools/stress-ng/stress-regex.c research

Purpose: implements `regex`, a hot CPU stressor that repeatedly compiles and executes a suite of POSIX extended regular expressions against representative text samples.

Important APIs, types, and functions: `stress_posix_regex_t` pairs regex strings with human descriptions, including deliberately pathological expressions, numeric formats, IP/time/date patterns, and common encodings. `stress_regex_text` holds candidate input strings. `stress_regex_rate()` aggregates per-regex counters and durations. `stress_regex()` owns compile/execute loops and metric publication.

Control flow: the stressor initializes timing/count/failure arrays, synchronizes, then loops through every regex while stress continues. Failed regex compilation is reported once per instance-zero worker and skipped in later passes. Successful compilations update compile timing, then run `regexec` against every sample string and record timing/count for matches. `regfree` releases each compiled regex. If no regex compiles successfully, the loop exits. Final metrics report aggregate `regcomp`/`regexec` rates and per-pattern compile rates.

State and persistence: all state is stack arrays and transient `regex_t` objects freed each pass. There are no persistent side effects.

Dependencies and integration: gated by `<regex.h>` and POSIX regex APIs: `regcomp`, `regerror`, `regexec`, and `regfree`. Uses stress-ng timing, metrics, and bogo helpers. Classified as CPU and hot, with max metric count sized to regex table length plus aggregates.

Risks: pathological patterns can be expensive or implementation-dependent. Because failed compile patterns are skipped after first report, a platform with strict regex semantics may have reduced workload. `regexec` timing only counts successful matches, not failed match attempts.

Test signals: compile failure informational logs, aggregate compile/exec rates, per-regex compile metrics, and bogo increments per regex compile attempt.
