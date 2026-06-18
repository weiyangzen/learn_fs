# sources/sync-backup/borg/docs/misc/logging.conf

Purpose: minimal Python logging configuration example for Borg's `BORG_LOGGING_CONF` environment variable.

Important APIs and control flow: follows `logging.config.fileConfig` INI sections: root logger, one `FileHandler`, one formatter. The root logger is `NOTSET`, the handler logs `INFO` and above, and formatted records include timestamp, level name, and message.

State and persistence: writes `borg.log` in the process current working directory with mode `w`, so each run truncates previous content.

Dependencies and integration points: referenced by the environment variables documentation. It depends on Python's logging configuration grammar and Borg honoring `BORG_LOGGING_CONF`.

Risks: relative log path can write into surprising locations. Truncating mode is dangerous for long-running automation. `NOTSET` on root delegates effective filtering to the handler, which may surprise users expecting Borg's default warning threshold.

Test signals: run Borg with `BORG_LOGGING_CONF` pointing at this file and confirm `borg.log` contains INFO records with the configured format.
