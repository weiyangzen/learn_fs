<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/constraints.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/constraints.conf

## Purpose

This is an mcstrans example constraint include file limiting invalid sensitivity/category combinations. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (10 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 0 mapping lines, and 1 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/constraints.conf -->
