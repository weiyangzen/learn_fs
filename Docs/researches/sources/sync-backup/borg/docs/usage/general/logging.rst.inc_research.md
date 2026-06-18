# sources/sync-backup/borg/docs/usage/general/logging.rst.inc

Purpose: general logging reference for Borg's stderr behavior, log levels, and custom logging configuration.

Important APIs and control flow: Borg writes logs to stderr by default, with WARNING as the built-in default level. `--debug`, `--info`/`-v`/`--verbose`, `--warning`, `--error`, and `--critical` set thresholds. `BORG_LOGGING_CONF` can load a Python logging config, and shell redirection captures stderr to a file.

State and persistence: default behavior writes no log files; user redirection or custom config can persist logs.

Dependencies and integration points: common options, return codes, JSON logging, logging.conf example, and Python logging.

Risks: stderr does not imply failure; automation must check log levels and return codes. `--error`/`--critical` may hide important warnings.

Test signals: log-level filtering tests, stderr output behavior, JSON log compatibility, and custom logging config loading.
