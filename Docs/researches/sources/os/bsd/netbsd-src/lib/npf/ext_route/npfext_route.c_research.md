# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_route/npfext_route.c

## Summary
Implements the userland constructor and parameter parser for the NPF `route` extension.

## Main Responsibilities
- Provide no-op initialization.
- Construct extension objects named `route`.
- Accept a parameter string and store it as `route-interface`.

## Key Interfaces
- `npfext_route_init()`.
- `npfext_route_construct(const char *name)`.
- `npfext_route_param(nl_ext_t *ext, const char *param, const char *val)`.

## Risks
The parameter is not validated as an existing interface in this userland parser. Interface validation, if any, must occur later.
