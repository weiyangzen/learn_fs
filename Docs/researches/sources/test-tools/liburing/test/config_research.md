# sources/test-tools/liburing/test/config

Purpose: template for liburing test-runner local configuration. It documents `TEST_EXCLUDE`, associative `TEST_MAP`, and `TEST_FILES` settings to map destructive or external-resource tests to files/devices.

Control flow: no executable behavior in the template; users copy it to `config.local` and uncomment variables. State/persistence comes only from copied local configuration. The main risk is accidental configuration of real devices that tests may erase or overwrite; the file's warning comments are its primary safety signal.
