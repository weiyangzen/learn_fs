# sources/test-tools/cthon04/special/dupreq.c

## Purpose
checks duplicate/lost replies for non-idempotent create/link/unlink sequences by repeatedly creating `name1`, hard-linking `name2`, then unlinking both names.

## Important APIs, Types, and Functions
`main()` parses `count name`, uses `creat()`, `link()`, `unlink()`, failure counters, and DOS/Win skip logic.

## Control Flow and State
A countdown loop performs create, link, unlink secondary, unlink primary, increments per-operation counters, and reports aggregate failures without aborting each iteration.

## Persistence and Dependencies
temporary `<name>1` and `<name>2` files are created and removed each pass. Dependencies: Unix hard links, POSIX file creation/unlink, and optional DOS/Win exclusion.

## Integration Points, Risks, and Test Signals
It integrates with the special idempotency tests. Risks are name collisions and unsupported hard links; signals are zero bad create/link/unlink counts.
