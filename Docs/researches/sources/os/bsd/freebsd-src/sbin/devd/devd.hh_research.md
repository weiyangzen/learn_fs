# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.hh

## Purpose
Declares the C++ object model for `devd`.

## Main Elements
- `var_list`: scoped event/global variable table.
- `eps`: abstract event-processing statement.
- `match`, `media`, `action`: concrete statement types.
- `event_proc`: priority-tagged group of match/action statements.
- `config`: stores directories, pidfile, variable stack, rule vectors, parsing, expansion, and event lookup methods.

## Dependencies And Integration
Implemented by `devd.cc`. Separates parser-facing construction from runtime matching/execution.
