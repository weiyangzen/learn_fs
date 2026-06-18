<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/Makefile -->
# sources/sync-backup/rsync/support/Makefile

Purpose: tiny support-directory makefile that builds the `savetransfer` helper.

Important APIs/types/functions: targets are `all`, `savetransfer`, and `clean`. `all` depends on `savetransfer`; `savetransfer` links from `savetransfer.o`; `clean` removes object files and the executable.

Control flow: normal make implicit rules compile `savetransfer.c` into `savetransfer.o` and link it. No custom compiler flags are specified here.

State and persistence behavior: produces local build artifacts `savetransfer.o` and `savetransfer`; `clean` removes them.

Dependencies and integration points: depends on make's built-in C rules and rsync's headers via `savetransfer.c`. It is a convenience build hook for support tooling, not the main rsync build system.

Risks: because it relies on implicit rules, unusual build environments may miss include paths or feature macros expected by `savetransfer.c`. It does not express header dependencies.

Test signals: `make -C support` should produce `savetransfer`, and `make -C support clean` should remove it.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/Makefile -->
