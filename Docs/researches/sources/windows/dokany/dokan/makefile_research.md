# File Research: sources/windows/dokany/dokan/makefile

Minimal Windows NT DDK makefile shim.

Key contents:
- Warns that source membership should be edited elsewhere.
- Includes `$(NTMAKEENV)\makefile.def`.
- Sets `C_DEFINES = /DUNICODE`.

Role:
- Legacy DDK build integration for the Dokan component.
