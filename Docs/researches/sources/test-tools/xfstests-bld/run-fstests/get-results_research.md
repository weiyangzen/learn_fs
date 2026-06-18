# sources/test-tools/xfstests-bld/run-fstests/get-results

Purpose: summarizes xfstests log files by grepping high-signal lines, with an optional failures-only mode that detects a missing `END` marker.

Important behavior: default regexp captures kernel version, command line, FSTEST/MNTOPTS/CPU/MEM metadata, BEGIN/END, mount/mkfs options, ext4 errors, warnings, run/failure/pass lines, inconsistent output, and shutdown reason. `--failures` narrows the regexp and enables missing-END detection.

Control flow: parses `--summary` or `--failures`, selects input files from arguments or latest `logs/log.*`, runs `grep -E`, and in failures mode compares counts of `BEGIN` and `END` lines.

State/persistence: read-only except stdout. No temp files.

Dependencies/integration: used by `gce-xfstests get-results --summary/--failures` and manually against local logs.

Risks: grep-based parsing is format-fragile. Missing-END detection only reports the last BEGIN if counts differ and does not pair tests structurally.

Test signals: fixture logs with pass/fail/incomplete cases should validate summary and failures mode.
