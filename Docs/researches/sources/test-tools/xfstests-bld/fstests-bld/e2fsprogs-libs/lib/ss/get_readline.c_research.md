# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/get_readline.c

## Purpose
`get_readline.c` optionally loads readline/editline support at runtime for libss interactive sessions.

## Important APIs, Types, and Functions
Public function is `ss_get_readline()`. Internal `ss_release_readline()` tears down a loaded handle. It probes libraries from `SS_READLINE_PATH` or a default colon-separated list.

## Control Flow
When `HAVE_DLOPEN` is enabled and no handle is loaded, it tries each library with `dlopen()`, resolves `readline`, `add_history`, redisplay and completion functions, sets readline global name/completion hooks when available, and stores a shutdown callback.

## State, Persistence, Dependencies, Risks, and Test Signals
State is stored in `ss_data` function pointers and `readline_handle`. Dependencies include `dlopen`, `dlsym`, `ss_safe_getenv()`, and optional readline-compatible ABI. Risks include ABI mismatch across libreadline/libedit versions, environment path trust limited by secure getenv, and silent fallback to stdio. Test signals are interactive prompt history/completion when a supported library is present and clean fallback when absent.
