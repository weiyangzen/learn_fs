# sources/test-tools/kdevops/callback_plugins/__init__.py

Purpose: package marker for kdevops Ansible callback plugins.

Important APIs/types/functions: the file is empty and exports no symbols.

Control flow: none.

State/persistence behavior: none.

Dependencies/integration: allows Python/Ansible tooling to treat `callback_plugins` as an importable package on runtimes that still care about package markers, and colocates `lucid.py` as a callback plugin.

Risks/test signals: no direct risks. Test signal is Ansible discovering the adjacent callback plugin when this directory is on the callback plugin path.
