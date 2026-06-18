## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/ProgressBar.java

Purpose: background progress reporter for Freon command execution.

Important APIs/types/functions: constructors accept output stream, max value, current value supplier, interactive flag, and real-time message supplier. Public methods: `start`, `shutdown`, `terminate`, and `print`. Internal methods render interactive or log-style progress.

Control flow: `start` launches one thread. The thread prints an initial line, loops once per second while running and current value is below max, prints current progress, then prints final state and marks stopped. `shutdown` waits for natural completion; `terminate` stops early. Interactive mode renders carriage-return progress bar; noninteractive mode logs percentage.

State and persistence behavior: volatile `running` and `startTime`; no persistence. Output goes to `PrintStream` or logger.

Dependencies and integration points: created by `BaseFreonGenerator.init`; real-time supplier can include command-specific rates such as `OmMetadataGenerator`.

Risks: percent divides by `maxValue`; max should be positive. Interactive bar uses block characters and width proportional to percent; log mode can emit repeated progress logs. `Thread` cannot be restarted after termination.

Test signals: `TestProgressBar` likely checks lifecycle and output behavior for interactive/noninteractive modes.
