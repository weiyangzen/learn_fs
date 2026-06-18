# sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c

Purpose: this fixture exercises switch-scope extraction and coverage mapping for a synthetic syscall and helper.

Important APIs and flow: it defines `COVER_IOCTL1` through `COVER_IOCTL4`, a static `cover_helper(int cmd)` with a switch over `COVER_IOCTL3` and `COVER_IOCTL4`, and `SYSCALL_DEFINE1(cover, int cmd)` with switch cases for all four constants. Cases 3 and 4 call the helper.

State and persistence: there is no persistent state. Local `tmp` variables test return-value fact extraction and branch-local increments.

Dependencies and integration: includes the fixture `syscall.h` macro that expands to `__do_sys_cover`. Its paired JSON and golden generated descriptions verify declextract's interpretation.

Risks: this is deliberately simple; it does not cover default cases, nested ranges, or real kernel macros.

Test signals: paired `cover.c.json` should expose functions, constants, syscall args, switch scopes, helper calls, and argument-flow facts.
