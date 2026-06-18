# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/__init__.py

## Purpose
This module defines the base class and dynamic plugin loader for ntlmrelayx protocol attacks. It discovers attack modules in the package, imports them, extracts their advertised attack classes, and registers them by protocol name in `PROTOCOL_ATTACKS`.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACKS` is the global registry mapping protocol/plugin names to attack classes.
- `_wrap_run_with_identity()` decorates attack `run()` methods with identity logging context when target and relay client information are available.
- `ProtocolAttack(Thread)` is the base class. It stores `config`, `client`, parsed `domain`, parsed `username`, optional `target`, and optional `relay_client`; subclasses are daemon threads.
- `ProtocolAttack.__init_subclass__()` wraps subclass-defined `run()` methods automatically.

## Control Flow
On import, the module scans files under `impacket.examples.ntlmrelayx.attacks`, imports each non-`__` Python file, reads `PROTOCOL_ATTACK_CLASS` or `PROTOCOL_ATTACK_CLASSES`, then registers each class under every value in its `PLUGIN_NAMES`. Import/logging errors are swallowed into debug logs so one broken plugin does not prevent loading others.

## State and Persistence Behavior
Global registry state is populated at import time. Each attack instance is a daemon `Thread`, although subclasses often call `run()` directly in relay control flow. The identity wrapper affects logging context only during `run()`.

## Dependencies and Integration Points
It depends on `importlib.resources.files`, `os`, `sys`, `threading.Thread`, `impacket.LOG`, and `identity_context`. It is imported by all attack modules and by ntlmrelayx orchestration to find the right attack for a relayed protocol.

## Risks and Edge Cases
- Import-time dynamic discovery can trigger side effects in every attack module.
- Registration silently ignores malformed plugins except for debug logs.
- `ProtocolAttack.__init__` assumes usernames contain `domain/user`; a malformed identity without `/` raises.
- Automatic `run()` wrapping can surprise subclasses that depend on exact function attributes.

## Test Signals
Tests should verify registry population, multiple-class registration, malformed plugin handling, identity-context formatting, daemon thread setup, and username/domain parsing error behavior.
