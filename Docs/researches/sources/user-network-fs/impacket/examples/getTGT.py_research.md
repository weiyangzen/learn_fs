# sources/user-network-fs/impacket/examples/getTGT.py

## Purpose

`getTGT.py` requests a Kerberos TGT, or optionally a service ticket directly through AS-REQ via `-service`, and saves the result as a ccache file. It supports password, NTLM hashes, AES key, KDC IP override, and configurable Kerberos principal name type.

## Important APIs, Types, and Functions

`GETTGT.__init__()` stores the target username, password, domain, hashes, AES key, KDC host, requested service, and options. `saveTicket(ticket, sessionKey)` creates a `CCache`, populates it with `fromTGT()`, and saves `<username>.ccache`. `run()` builds a `Principal`, calls `getKerberosTGT()` with credentials and optional `serverName`, then saves the ticket.

## Control Flow

The CLI parses `[domain/]username[:password]`, initializes logging, prompts for a password when needed, validates a domain and `-principalType`, then executes `GETTGT.run()`. Hashes are split into LM/NT strings and converted with `unhexlify()` at the Kerberos call boundary. The `-service` option is passed as `serverName`, enabling AS-REQ service-ticket style requests supported by the underlying Impacket function.

## State and Persistence Behavior

The script writes exactly one ccache file named after the username in the current directory. It does not mutate remote state. It may read a password from stdin. Ticket and session key material live in memory until saved.

## Dependencies and Integration Points

It depends on Impacket `getKerberosTGT()`, `CCache`, Kerberos `Principal`, constants, `parse_identity()`, and the shared logger. The output ccache integrates with other Impacket examples and system Kerberos tooling through `KRB5CCNAME`.

## Risks and Edge Cases

`GETTGT.run()` references global `options.principalType` instead of `self.__options.principalType`, so imported or reused class instances depend on a module-level CLI variable. The output filename can collide across domains or overwrite an existing ccache for the same username. `domain is None` is rejected, but an empty string can pass depending on `parse_identity()` behavior. Invalid hash strings fail at `unhexlify()`. The saved ccache uses `oldSessionKey`, matching Impacket convention, but tests should guard that behavior if `getKerberosTGT()` changes.

## Test Signals

Tests should mock `getKerberosTGT()` and `CCache.saveFile()` to verify credential conversion, service forwarding, output naming, and principal type handling. A regression test should instantiate `GETTGT` without global `options` to catch the class/global coupling. Integration tests should request TGTs with password, hashes, AES key, non-default principal type, and `-service`.
