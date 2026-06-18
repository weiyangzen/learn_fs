# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/listen.c

## Purpose
`listen.c` implements the interactive ss read-execute loop, quit handling, SIGINT recovery, and optional readline completion support.

## Important APIs, Types, and Functions
Public functions are `ss_listen()`, `ss_abort_subsystem()`, `ss_quit()`, and, when `HAVE_DLOPEN`, `ss_rl_completion()`. Internal helpers include prompt and interrupt signal handlers plus command-name completion generation.

## Control Flow
`ss_listen()` sets current invocation state, installs SIGINT/SIGCONT handling, reads lines via readline or `fgets()`, adds history, executes the line, reports unknown requests, and exits on EOF or `abort`. SIGINT longjmps back to the prompt. Completion iterates request tables and command aliases.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes static `current_info`, `listen_jmpb`, `sig_cont`, and per-invocation abort/exit fields. Dependencies include signals, setjmp, readline pointers, and `ss_execute_line()`. Risks include non-reentrant static state, longjmp across library frames, signal-handler safety, and global current-info completion assumptions. Test signals are Ctrl-C recovery, EOF handling, `quit`, unknown-command diagnostics, and readline completion.
