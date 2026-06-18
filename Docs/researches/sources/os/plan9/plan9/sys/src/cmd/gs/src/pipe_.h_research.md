# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/pipe_.h

Small portability wrapper for `popen` and `pclose`.

Behavior:

- Includes `stdio_.h`.
- On `__WIN32__`, maps `popen` to Ghostscript’s `mswin_popen`, because old MSVC `_popen` implementations are noted as broken for Ghostscript’s needs. `pclose` maps to `_pclose`.
- On non-Windows platforms, declares `popen` without a prototype argument list due to inconsistent system headers, and declares `pclose(FILE *)`.

This is portability support for process pipes. It is adjacent to OS integration but contains no filesystem implementation logic.
