# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_provision_performance.py

Purpose: this performance test times and validates several `samba-tool domain provision` entry points and option combinations in temporary target directories.

Important APIs/types/functions: `UserTests.setUp()` creates a tempdir, `tearDown()` removes it, `_test_provision_subprocess()` invokes `bin/samba-tool domain provision` with `--targetdir`, `--realm`, `--domain`, and `--use-ntvfs`, while `test_02_00_provision_cmd_sambatool()` calls the in-process `samba_tool()` API. Other tests cover overwrite, server roles, blank provision, and partitions-only provision.

Control flow: the module parses options and credentials but does not use the supplied host beyond the shared harness. Each test provisions into either the shared tempdir or a named child directory. Test methods execute through `TestProgram` or the ancient subunit fallback.

State and persistence behavior: all provisioned databases and generated files live under the per-test tempdir and are removed during `tearDown()`. The subprocess path may leave partial state if provisioning crashes before cleanup.

Dependencies and integration points: integrates with both the CLI `bin/samba-tool` and Python `samba_tool` command dispatcher. It depends on local build artifacts, the provision subsystem, temp filesystem performance, and optional NTVFS behavior.

Risks: `_test_provision_subprocess()` contains `if options: options.extend(options)` and never appends the provided options to `cmd`, so server-role, blank, and partitions-only subprocess tests do not actually pass their requested options. Provisioning performance can vary heavily with filesystem and build configuration.

Test signals: pass/fail reflects command success. The external harness must measure duration; this file itself does not assert timing thresholds.
