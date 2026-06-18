# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_log/npfext_log.c

## Summary
Implements the userland constructor and parameter parser for the NPF `log` extension.

## Main Responsibilities
- Provide `npfext_log_init()` with no initialization work.
- Construct extension objects named `log`.
- Accept a parameter interpreted as an interface name.
- Resolve the interface index with `if_nametoindex()`.
- If missing, create the interface via `SIOCIFCREATE`, bring it up with `SIOCSIFFLAGS`, and resolve again.
- Store the interface index as extension parameter `log-interface`.

## Key Interfaces
- `npfext_log_init()`.
- `npfext_log_construct(const char *name)`.
- `npfext_log_param(nl_ext_t *ext, const char *param, const char *val)`.

## Risks
Parameter parsing has side effects: an unknown interface name can create and enable an interface. Errors are returned as errno values and also warned to stderr through `warn()`.
