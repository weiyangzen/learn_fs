# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRegistry.cc

## Purpose
`XrdNetRegistry.cc` implements pseudo-host registration for contact lists. Names beginning with `%` can expand into one or more real `host:port` entries, optionally rotating returned order across calls and supporting aliases.

## Important APIs, Types, and Functions
Private `regEntry` stores the pseudo-host name, host vector, parent alias pointer, reference counter, rotate flag, and per-entry RW lock. Public `Register()` overloads accept arrays or comma-separated strings. `GetAddrs()` resolves a registered pseudo-host through `XrdNetUtils`. Private `Resolve()` validates targets and `SetAlias()` creates aliases.

## Control Flow
Registration validates arguments and resolves every target unless resolution reports a dynamic host. String registration splits comma-separated hosts, requires ports, and delegates to array registration or alias creation. `GetAddrs()` finds the entry under a global mutex, increments the rotation counter if needed, takes an entry read lock, releases the global mutex, resolves the list with optional force behavior, then releases the entry lock.

## State and Persistence
Registry entries are process-global linked-list nodes and are never deleted. Updates replace an entry's host vector under its write lock. Aliases point to parent entries.

## Dependencies and Integration Points
It depends on `XrdNetAddr`, `XrdNetUtils`, and XrdSys locks. `XrdNetUtils::GetAddrs(std::string...)` dispatches `%` names here. `XrdSsiClient` registers multi-contact pseudo-hosts.

## Risks and Test Signals
`regEntry::Find()` compares `const char*` to `std::string` via overloaded equality and follows aliases, which should be tested carefully. Rotation uses an 8-bit `refs` counter exposed as unsigned int, so wraparound is expected. Tests should cover invalid names, missing ports, unresolved hosts, dynamic hosts, replacing entries, alias rules, rotation ordering, force resolution, concurrent get/update, and unregistered lookup.
