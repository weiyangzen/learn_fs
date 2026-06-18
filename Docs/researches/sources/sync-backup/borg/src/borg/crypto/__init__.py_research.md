# sources/sync-backup/borg/src/borg/crypto/__init__.py

Purpose: empty package initializer for `borg.crypto`.

Important APIs: no symbols, imports, side effects, or state are defined in this file.

Control flow and state: none. Importing `borg.crypto` only initializes the package namespace.

Dependencies and integration: crypto functionality is implemented in sibling modules such as `key.py`, `keymanager.py`, `file_integrity.py`, and low-level crypto modules.

Risks: minimal. If consumers expect package-level re-exports, they are not provided here.

Test signals: import smoke coverage is sufficient; substantive crypto tests target sibling modules.
