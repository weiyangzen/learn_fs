# sources/security-integrity/selinux/python/sepolicy/setup.py
# sources/security-integrity/selinux/python/sepolicy/setup.py

Purpose: setuptools metadata for packaging the `sepolicy` Python package.

Important APIs and control flow: calls `setup()` with name `sepolicy`, version `3.11-rc2`, description, author metadata, package list (`sepolicy`, `sepolicy.templates`, `sepolicy.help`), and package data for glade/help assets.

State and persistence: creates build/install artifacts when invoked by packaging tools; no runtime state.

Dependencies and integration points: depends on `setuptools` and package directory layout. It integrates with the wider SELinux Python build/install process.

Risks and test signals: package data omissions would break GUI/help assets after install. No direct test targets setup metadata.
