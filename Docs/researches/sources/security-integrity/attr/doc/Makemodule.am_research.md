## sources/security-integrity/attr/doc/Makemodule.am

Purpose: documentation distribution fragment.

It adds `CHANGES`, `COPYING`, and `COPYING.LGPL` to installed distributed docs, and includes generated `INSTALL` in extra distribution. There is no runtime state. Dependencies are Automake variables from the top-level file. Risks are missing `doc/INSTALL` if bootstrap did not copy it. Test signal is `make distcheck` or distribution tarball inspection.
