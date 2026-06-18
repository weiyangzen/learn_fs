# sources/security-integrity/libcap/progs/old/execcap.c

Purpose: legacy wrapper that sets the current process capabilities from text and then execs another command.

Important APIs/functions: `usage()` documents that it is not safe as setuid-root. `main()` rejects setuid-root use, parses `argv[1]` with `cap_from_text()`, applies it with `cap_set_proc()`, then `execvp()`s `argv[2:]`.

Control flow: any validation, parse, or capability set failure prints an error and exits through usage. Successful `execvp()` never returns.

State and dependencies: mutates current process capability sets and inherits all environment variables into the target. Depends on libcap and exec semantics.

Risks and test signals: old example code lacks modern IAB/ambient/bounding handling and intentionally warns against setuid deployment. It is best treated as historical sample code, not a hardened launcher.
