# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.h

## Scope

Public header for the Citrus `mapper_zone` module.

## APIs

- Defines include guard `_CITRUS_MAPPER_ZONE_H_`.
- Declares the mapper getops entry point through `_CITRUS_MAPPER_GETOPS_FUNC(mapper_zone)` inside `__BEGIN_DECLS` / `__END_DECLS`.

## Dependencies And Invariants

- Requires Citrus mapper macro definitions from including context.
- Contains no data structures or inline behavior; ABI exposure is limited to the getops symbol.
