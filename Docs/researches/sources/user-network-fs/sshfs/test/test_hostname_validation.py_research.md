# sources/user-network-fs/sshfs/test/test_hostname_validation.py

Purpose: focused pytest module validating that sshfs rejects dash-prefixed hostnames that could be interpreted as SSH options.

Important APIs/types/functions: executable self-runner under `__main__`; imports `subprocess`, `base_cmdline`, `basename`; tests `test_reject_option_injection_in_hostname` and `test_reject_dash_host_after_doubledash`.

Control flow: each test creates a temporary mount directory, constructs an sshfs command line pointing at the built executable, runs it with captured output and 10-second timeout, and asserts nonzero exit plus `invalid hostname` in stderr. One case uses bracketed host syntax resolving to `-oProxyCommand=...`; the other passes a dash-prefixed source after `--`.

State and persistence behavior: creates temporary directories only; no mount should occur because validation fails before connecting.

Dependencies and integration points: directly tests `find_base_path`/argument parsing behavior in `sshfs.c`, using test utilities from `util.py`.

Risks: depends on exact stderr wording. It covers dash-host rejection but not all command injection surfaces such as custom `ssh_command` tokenization or unusual bracket syntax.

Test signals: both tests must fail fast with nonzero return and `invalid hostname`, proving the host parser does not pass dash-prefixed hosts through to ssh.
