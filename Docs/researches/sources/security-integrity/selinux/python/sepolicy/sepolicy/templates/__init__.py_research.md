# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/__init__.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/__init__.py

Purpose: package initializer for `sepolicy.templates`.

Important APIs and control flow: it contains copyright/license comments only and defines no functions, classes, constants, imports, or side effects.

State and persistence: none.

Dependencies and integration points: its presence marks the directory as an importable Python package used by `setup.py` and policy generation code that imports individual template modules.

Risks and test signals: low risk beyond packaging visibility. No direct tests are expected; failures would show as import errors for `sepolicy.templates`.
