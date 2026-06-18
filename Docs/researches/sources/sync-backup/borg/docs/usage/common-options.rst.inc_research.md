# sources/sync-backup/borg/docs/usage/common-options.rst.inc

Purpose: shared generated snippet listing Borg common CLI options.

Important APIs and control flow: covers help, log level selectors, debug topics, progress, unit formatting, JSON logs, lock wait, version/rc display, umask, remote path, upload throttling/buffering, profiling, SSH command selection, and repository selection via `-r/--repo`.

State and persistence: affects process-level behavior: log emission, JSON log format, lock wait timing, local umask, remote invocation, profiling output file, and selected repository.

Dependencies and integration points: included by generated command help tables and tied to jsonargparse common option definitions, logging setup, remote repository transports, and config/env precedence.

Risks: option ordering matters elsewhere in Borg. Log JSON and profiling outputs are machine-facing contracts. Remote path and `--rsh` can change execution target and security posture.

Test signals: generated snippets should update when common parser options change; CLI tests should verify each common option remains accepted before subcommands and in documented positions.
