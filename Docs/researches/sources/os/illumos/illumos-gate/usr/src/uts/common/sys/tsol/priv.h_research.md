# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/priv.h

## Purpose
Trusted Extensions compatibility privilege header mapping old privilege macros and names to illumos privilege sets.

## Main Interfaces
- Defines `priv_ftype` for file privilege typing.
- Maps legacy macros such as `PRIV_ASSERT`, `PRIV_CLEAR`, `PRIV_EQUAL`, `PRIV_EMPTY`, `PRIV_FILL`, `PRIV_ISASSERT`, `PRIV_ISEMPTY`, `PRIV_ISFULL`, `PRIV_ISSUBSET`, `PRIV_INTERSECT`, `PRIV_INVERSE`, and `PRIV_UNION` onto `priv_*set` operations.
- Defines Trusted Extensions privilege name aliases including file label upgrade/downgrade, audit, translated labels, and window-system privileges.

## Dependencies And Relationships
Includes `sys/priv.h`. Used by older TSOL-aware code that expects historical privilege macro names.

## Research Notes
Most content is compatibility mapping. The privilege names are string constants passed into the regular illumos privilege framework.
