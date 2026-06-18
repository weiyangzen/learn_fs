# sources/sync-backup/borg/src/borg/cockpit/__init__.py

Purpose: marks the `borg.cockpit` package and documents that it contains the Borg Cockpit Textual terminal UI.

Important APIs: no runtime APIs, imports, exports, or state are defined. The module docstring describes the package-level role.

Control flow and state: no control flow or persistence. Importing the package only executes the docstring.

Dependencies and integration: package siblings (`app.py`, `runner.py`, `theme.py`, `translator.py`, `widgets.py`) provide the actual UI. This file enables normal package import semantics.

Risks: minimal. If public exports are later expected from `borg.cockpit`, they are currently absent.

Test signals: import smoke tests are sufficient; functional coverage belongs to the app, runner, and widgets modules.
