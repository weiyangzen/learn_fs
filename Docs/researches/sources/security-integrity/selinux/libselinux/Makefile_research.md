# sources/security-integrity/selinux/libselinux/Makefile

## Purpose
This is the top-level recursive makefile for `libselinux`. It configures feature flags, PCRE integration, large-file support, OS/compiler detection, and delegates build/install/clean targets to subdirectories.

## Important APIs, types, and functions
Key variables include `SUBDIRS = include src utils man`, `PKG_CONFIG`, `DISABLE_SETRANS`, `DISABLE_RPM`, `ANDROID_HOST`, `LABEL_BACKEND_ANDROID`, `USE_PCRE2`, `USE_LFS`, `PCRE_MODULE`, `PCRE_CFLAGS`, `PCRE_LDLIBS`, `LFS_CFLAGS`, `OS`, and `COMPILER`. Targets `all`, `install`, `relabel`, `clean`, and `distclean` loop over `SUBDIRS`. Wrapper targets delegate Python/Ruby binding generation and cleanup to `src`.

## Control flow
Make evaluates feature variables, appends preprocessor flags, queries `pkg-config` for PCRE flags, exports settings to sub-makes, detects clang versus gcc from `$(CC) -v`, and runs each subdirectory make target sequentially, aborting on first failure.

## State and persistence behavior
The makefile itself persists no state. Build outputs, installed headers/libraries/man pages, generated wrappers, and cleanup are handled by subdirectory makefiles using the exported variables. Environment overrides allow packaging systems to control optional dependencies.

## Dependencies and integration points
It integrates with `include`, `src`, `utils`, and `man` subtrees, `pkg-config`, PCRE or PCRE2 development packages, compiler tooling, and platform-specific Android feature selection.

## Risks and edge cases
`pkg-config` is evaluated during makefile expansion, so missing PCRE packages can produce empty or bad flags before any target logic runs. `ANDROID_HOST=y` forces some disables, but `DISABLE_BOOL` is otherwise only conditionally referenced and not initialized near the top. Compiler detection by grepping `$(CC) -v` is heuristic. The `test` target is declared but empty.

## Test signals
Build matrix tests should cover PCRE2 and PCRE modes, Android host mode, disabled RPM/setrans/bool/X11 options, large-file support toggling, clang/gcc detection, install staging through `DESTDIR`, and recursive failure propagation from each subdir.
