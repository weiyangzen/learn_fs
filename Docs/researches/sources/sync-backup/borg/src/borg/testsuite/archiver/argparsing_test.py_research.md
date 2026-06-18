# sources/sync-backup/borg/src/borg/testsuite/archiver/argparsing_test.py

Purpose: tests Borg archiver argument parsing, forced-command merging, REST backend restrictions, duplicate/highlander options, filter validation, and common-option propagation across subcommands.

Important APIs/types/functions: tests use `Archiver.get_args`, `Archiver.check_rest_restrictions`, `ArgumentParser`, `flatten_namespace`, `PathNotAllowed`, and the CLI `cmd` wrapper. `TestCommonOptions` defines an artificial common-option set and parser/subparser fixtures to exercise Borg's custom parser machinery.

Control flow: `test_bad_filters` checks invalid archive filters return parse error. `test_highlander` confirms repeated `--umask` combinations fail while single default/custom values work. `test_get_args` combines forced SSH command arguments with `SSH_ORIGINAL_COMMAND`-like strings, rejecting attempts to override path/repository restrictions, change subcommands, or enable REST mode when not forced. It also preserves REST `--backend` so restriction checks can validate it. `test_check_rest_restrictions` accepts unrestricted and allowed `FILE:` backends and raises for outside, non-exact, or non-FILE backends. `TestCommonOptions` verifies options before and after subcommands merge into one namespace and invalid placement is rejected.

State and persistence behavior: most tests are parser-only. Some create a repository/archive to exercise real CLI validation. No durable state beyond fixture repositories.

Dependencies and integration points: integrates with Borg's top-level archiver parser, serve/REST security restrictions, helper path authorization, and common option infrastructure shared by all commands.

Risks: parser tests are sensitive to option defaults, subcommand parser internals, and exact error wording. Security-sensitive forced-command tests must remain conservative because mistakes could permit SSH users to escape restrictions.

Test signals: parse results, exception types, and CLI exit codes provide strong signals for argument handling and serve restriction safety.
