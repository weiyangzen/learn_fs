<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/subunitrun -->
# sources/user-network-fs/samba/source4/scripting/bin/subunitrun

Purpose: deprecated wrapper for running Samba Python tests through the Samba subunit test runner while still accepting Samba-specific credentials and loadparm options.

Important APIs/types/functions: `SubunitOptions`, `TestProgram`, `CredentialsOptions`, `SambaOptions`, and `samba.tests.cmdline_credentials`.

Control flow: sets SIGINT to default, prepends `bin/python`, parses test, credential, Samba, and subunit options, initializes command-line credentials unless listing tests, injects `--load-list` into runner args when supplied, and dispatches `TestProgram`.

State and persistence behavior: no persistent state. It stores credentials in the in-process `samba.tests` module for tests.

Dependencies and integration points: integrates test modules under `python/samba/tests`, subunit output, and older blackbox/selftest invocations that pass credentials to this wrapper.

Risks: deprecated behavior can diverge from `python -m samba.subunit.run`. Tests depending on global credentials can hide fixture coupling.

Test signals: subunit output, list-tests output, and successful import/execution of named test modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/subunitrun -->
