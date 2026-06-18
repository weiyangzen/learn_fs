# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/pipe_.h

Portable declaration wrapper for `popen` and `pclose`. It includes Ghostscript’s `stdio_.h` wrapper and normalizes Windows versus non-Windows handling.

On Win32 it redirects `popen` to Ghostscript’s `mswin_popen` implementation because historical MSVC `_popen` versions were considered broken for Ghostscript’s needs, while `pclose` maps to `_pclose`. On non-Windows platforms it declares `popen` without a prototype argument list because old platform headers were inconsistent.

Dependencies are C stdio and platform macros such as `__WIN32__`.

Filesystem relevance is indirect: this supports process pipe IO for userland Ghostscript streams, not kernel pipes or VFS.
