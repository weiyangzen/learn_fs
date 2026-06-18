## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/REPL.java

Purpose: JLine/picocli read-eval-print loop used by `Shell` interactive and batch modes.

Important APIs and control flow: constructor builds a dumb terminal, registers picocli commands and `help` with `SystemRegistry`, configures a `LineReader` with completion and auto-listing, optionally preloads batch commands, prints welcome lines for interactive mode, then loops reading and executing commands until EOF or batch exhaustion. User interrupts are ignored; other exceptions are traced through the registry. It prints a blank line before the next prompt.

State and dependencies: terminal/session state only. Depends on JLine terminal/reader/system registry and picocli shell integration.

Risks and test signals: batch mode relies on outer `Shell` exception handling for exit behavior. Dumb terminal mode favors broad compatibility. No direct tests in this subset.
