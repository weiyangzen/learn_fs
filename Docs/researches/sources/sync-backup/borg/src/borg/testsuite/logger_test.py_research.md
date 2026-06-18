# sources/sync-backup/borg/src/borg/testsuite/logger_test.py

Purpose: tests Borg logger setup, parent-module discovery, multiple logger names, and lazy logger proxy methods.

Important APIs and control flow: module-level `logger = create_logger()` is exercised with a `StringIO` handler from `setup_logging`. Tests assert formatted output names for module logger and explicit `logging.getLogger` calls, truncate/reset the stream between cases, check `find_parent_module()`, and call all proxy methods including `exception`.

State and persistence: mutates process logging handlers/levels and captures in-memory stream output.

Dependencies and integration points: depends on `borg.logger.find_parent_module`, `create_logger`, `setup_logging`, Python logging, and pytest fixtures. It affects CLI and internal log routing.

Risks: global logging state can leak between tests if setup does not isolate handlers. Output includes module names and is exact.

Test signals: exact stream contents, correct parent module, and no exceptions from lazy proxy methods.
