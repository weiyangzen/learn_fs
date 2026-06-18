# sources/user-network-fs/impacket/tests/conftest.py

Purpose: integrates the shared remote-test configuration with pytest. It adds a command-line/ini option for the remote configuration file and provides a class-scoped fixture that populates test classes with credential attributes.

Important APIs and functions: `pytest_addoption()` registers `--remote-config` and `remote-config` ini. `pytest_configure()` resolves those settings and, when present, calls `set_remote_config_file_path()` and `set_transport_config(config)`. The `remote` fixture calls `set_transport_config(request.cls)` for class tests.

Control flow: pytest startup parses options, then configuration is applied globally. For tests using `@pytest.mark.usefixtures("remote")` or class fixture injection, the class receives the same attributes expected by `RemoteTestCase` subclasses.

State and persistence behavior: no persistent files are written. It can mutate the pytest `config` object with credential attributes, and fixture execution mutates test classes.

Dependencies and integration points: depends on pytest hook semantics and local helpers from `tests.__init__`. It connects pytest option handling to unittest-style remote tests and complements direct `RemoteTestCase.set_transport_config()` calls in test `setUp()` methods.

Risks: `parser.addini(..., type="pathlist")` may return a list while `set_remote_config_file_path()` expects a file-like path value; callers usually use the command-line option. Applying credentials to pytest `config` can expose secrets to plugins inspecting config attributes. Missing config values fail before remote tests run.

Test signals: pytest collection and remote tests using `--remote-config` should use the specified file rather than the default or `REMOTE_CONFIG`.
