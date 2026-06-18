# sources/test-tools/stress-ng/core-opts.c

Purpose: central GNU long-option registry for the stress-ng command-line parser.

Important APIs/types: defines `const struct option stress_long_options[]`, mapping option names to `stress_op_t` enum values and argument requirements for global flags, stressor selectors, and per-stressor tuning options.

Control flow: no algorithmic flow beyond the sentinel `{ NULL, 0, NULL, 0 }`. Runtime parsing elsewhere passes this table to getopt-style logic and receives enum IDs.

State/persistence: immutable command-line metadata. It does not store parsed values.

Dependencies/integration: `stress-ng.h`, `core-opts.h`, `getopt.h`, and feature macros gating options such as `--perf`, `--pipe-size`, `--syslog`, and `--vm-populate`.

Risks: table and `stress_op_t` enum must stay synchronized; duplicate or mismatched IDs route parsing incorrectly; conditional entries affect CLI by platform; argument-required flags must match downstream parser expectations.

Test signals: help/stressor output, option parsing smoke tests, duplicate-name detection, feature-gated build matrices, and enum/table consistency checks.
