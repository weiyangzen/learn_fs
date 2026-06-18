# File Research: sources/os/bsd/netbsd-src/lib/lua/syslog/syslog.c

## Summary
Implements Lua bindings for syslog operations and constants.

## Main Responsibilities
- Wrap `openlog`, `syslog`, `closelog`, and `setlogmask`.
- Emit log messages with `"%s"` format to avoid format-string interpretation.
- Export syslog option, facility, and priority constants.
- Add module metadata fields.

## Key Interfaces
- `luaopen_syslog(lua_State *L)`.
- Lua functions: `openlog`, `syslog`, `closelog`, `setlogmask`.

## Risks
The binding exposes process-global syslog state. Lua callers can change log identity, facility, and mask for the hosting process.
