<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.h -->
# sources/security-integrity/selinux/libselinux/src/selinux_internal.h

## Purpose
Defines libselinux-wide internal portability, threading, errno, configuration, and compiler helper macros.

## Important APIs, Types, And Functions
Exports `require_seusers`, `selinux_page_size`, `has_selinux_config`, `SELINUXDIR`, `SELINUXCONFIG`, weak-pthread wrappers (`__selinux_once`, mutex/key helpers), `__pthread_supported`, fallbacks for `strlcpy`/`reallocarray`, sanitizer/deprecation macros, `fclose_errno_safe()`, `likely`/`unlikely`, `spaceship_cmp()`, and `SELINUX_PROTECT_ERRNO`.

## Control Flow
Macros conditionally call pthread functions only when linked, allowing builds without hard pthread dependencies.

## State And Persistence Behavior
Only extern declarations point to process-global state; no storage is defined here.

## Dependencies And Integration Points
Included broadly across libselinux. Threaded modules rely on these wrappers for optional pthread support and cleanup.

## Risks And Test Signals
Risks include weak-symbol behavior on unusual linkers, macros silently doing nothing without pthreads, and cleanup attribute compiler support. Build matrix tests with/without pthreads and fallback libc functions are important.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.h -->
