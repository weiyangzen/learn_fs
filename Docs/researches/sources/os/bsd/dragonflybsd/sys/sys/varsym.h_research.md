# File Research: sources/os/bsd/dragonflybsd/sys/sys/varsym.h

## Summary
Variant symlink data structures and kernel APIs.

## Main Responsibilities
- Defines `struct varsym`, `struct varsyment`, and `struct varsymset`.
- Defines variable levels for process, user, system, and internal prison scope.
- Defines scope masks and maximum name/data/set sizes.
- Declares kernel lookup, creation/replacement, reference drop, set init/clean, and symlink replacement helpers.

## Important Behavior
Variant symlink sets are TAILQ-backed and protected by a lock. Shared variable objects carry a reference count.

## Risks
Substitution length limits are fixed. Incorrect scope-mask handling could leak or hide per-user/process variant symlink values.
