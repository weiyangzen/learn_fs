# File Research: sources/virtualization/libblockdev/src/utils/logging.h

This public header declares shared logging utilities.

Definitions:
- Defines syslog-compatible numeric levels directly because GObject Introspection cannot use redefined syslog constants cleanly.
- Defines `BDUtilsLogFunc(level, msg)` callback type.
- Declares logging initialization, log-level setting, direct logging, formatted logging, and stdout/GLib logging helper.

Research relevance:
- Provides the log API consumed by execution utilities and plugins without requiring callers to include syslog constants through GI.
