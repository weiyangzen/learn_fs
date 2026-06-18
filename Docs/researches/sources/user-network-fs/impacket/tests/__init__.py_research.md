# sources/user-network-fs/impacket/tests/__init__.py

Purpose: provides the shared remote-test configuration layer used by Impacket integration tests. It stores the remote config path, loads `tests/dcetests.cfg` or a user-specified config, and applies credentials and target identifiers to test instances.

Important APIs and types: module globals include `remote_config_file_path`, `remote_config_section`, `remote_config_params`, and `remote_config_params_names`. Public helpers are `set_remote_config_file_path()`, `get_remote_config_file_path()`, `get_remote_config()`, and `set_transport_config()`. `RemoteTestCase` exposes `set_transport_config()` as a base-class method for unittest-style tests.

Control flow: config path resolution first honors the pytest-set module variable, then `REMOTE_CONFIG`, then defaults to `tests/dcetests.cfg`. `set_transport_config()` reads the `TCPTransport` section and sets `username`, `domain`, `serverName`, `password`, `machine`, and `hashes` on the target object. It splits NTLM hashes into text and binary LM/NT values. Optional branches load machine-account hashes and Kerberos AES keys.

State and persistence behavior: module state is limited to the selected config path. The loaded credentials are copied to test objects or pytest config objects at runtime. No files are written.

Dependencies and integration points: uses `ConfigParser`, environment variables, `binascii.unhexlify`, and `six.moves.configparser`. It is consumed by `conftest.py`, `tests.dcerpc.DCERPCTests`, WMI tests, and many SMB/RPC tests. The expected config schema is documented by `dcetests.cfg.template`.

Risks: missing options raise config parser errors at setup time. Hash parsing assumes `LM:NT` format when `hashes` is non-empty. Secrets are attached as plain object attributes. The default path is relative to the working directory, so running tests outside the repository can silently miss the intended config.

Test signals: healthy remote integration tests demonstrate this module loaded the correct target, domain, username, password/hash, server NetBIOS name, and optional machine-account credentials.
