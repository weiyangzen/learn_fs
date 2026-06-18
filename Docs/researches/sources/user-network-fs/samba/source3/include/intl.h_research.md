# sources/user-network-fs/samba/source3/include/intl.h

## Purpose
`intl.h` defines the `N_()` marker macro for translatable strings that should be extracted but not translated immediately.

## Important APIs, Types, And Functions
- `N_(x)` expands to `x`.

## Control Flow
No runtime flow. Code wraps static strings with `N_()` so translation tooling can find them while runtime receives the original literal.

## State And Persistence
No state.

## Dependencies And Integration Points
It integrates source strings with Samba's internationalization tooling and dynamic loading constraints.

## Risks
Using `N_()` where immediate translation is required leaves strings untranslated until later code calls the actual gettext function. Since it is a macro, it provides no type checking beyond expression use.

## Test Signals
Translation extraction tests should ensure `N_()` markers are picked up, and UI tests should verify marked strings are later translated at display time.
