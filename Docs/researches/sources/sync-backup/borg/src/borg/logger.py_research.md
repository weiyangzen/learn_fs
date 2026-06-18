# sources/sync-backup/borg/src/borg/logger.py

Purpose: central logging setup for Borg CLI, tests, remote serve, progress output, JSON logs, warnings redirection, and lazy module loggers.

Important APIs/types: `setup_logging` configures root and progress loggers from a config file or fallback handlers. `create_logger` returns `LazyLogger`, delaying real logger lookup until setup. `BorgQueueHandler` serializes records for remote transfer. `StderrHandler` follows current `sys.stderr`. `TextProgressFormatter`, `JSONProgressFormatter`, and `JsonFormatter` control output shape.

Control flow/state: `configured` gates lazy logger use. Setup reads `BORG_LOGGING_CONF`, falls back on failure, installs stream or queue handlers, configures `borg.output.progress`, optional debug file handlers, and redirects warnings through logging. `LazyLogger` proxies standard logging methods and moves Borg `msgid` into `extra`.

Dependencies/integration: all Borg modules use this module. `legacy.remote.RepositoryServer` drains `borg_serve_log_queue`; clients reconstruct remote `LogRecord`s. Progress helpers emit JSON to `borg.output.progress`.

Risks: logging before setup raises. Global logging state complicates tests and long-running serve processes. Progress formatters assume valid JSON messages. Queue record dictionaries must remain compatible with `logging.LogRecord`.

Test signals: fallback and JSON setup, config failure warning, early logger failure, warnings redirection, serve queue records, progress formatting, flush behavior, and `msgid` propagation.
