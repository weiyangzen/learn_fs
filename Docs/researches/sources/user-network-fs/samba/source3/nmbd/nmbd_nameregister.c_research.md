# sources/user-network-fs/samba/source3/nmbd/nmbd_nameregister.c

## Purpose
Implements asynchronous registration and refresh of Samba-owned NetBIOS names. It covers broadcast registration, WINS registration, multihomed WINS registration across all interface IPs, WINS failover by tag, and refresh of existing WINS records.

## Important APIs, Types, And Functions
Public APIs are `register_name()` and `wins_refresh_name()`. Key internals are `register_name_response()`, `register_name_timeout_response()`, `wins_registration_timeout()`, `multihomed_register_name()`, `multihomed_register_one()`, and `wins_next_registration()`.

## Control Flow
`register_name()` converts/truncates names into DOS NetBIOS limits, sets `NB_ACTIVE`, and chooses WINS multihomed registration for `unicast_subnet` or broadcast registration otherwise. Broadcast registration succeeds on timeout with no replies; a reply is a conflict except for a legacy Samba `WORKGROUP<1b>` hack. WINS registration expects a response, handles WACK, filters unexpected responder IPs, marks servers alive/dead, and calls standard plus caller callbacks. Multihomed WINS registration pre-adds unique names to unicast so WINS validation queries can succeed, then chains registrations for each interface IP and WINS tag.

## State And Persistence
Mutates response retry state, WINS liveness, and local namelists through standard callbacks. Unicast self records may be created before WINS acceptance to satisfy validation. Refresh uses the same response path.

## Dependencies, Risks, And Test Signals
Depends on packet queues, WINS server selection/failover, namelist callbacks, charset conversion, and subnet enumeration. Risks include premature unicast insertion, name truncation surprises, and treating all-WINS-down timeout as success. Test signals include broadcast conflict vs timeout success, WACK delay, response-source filtering, WINS failover, multihomed chaining, and refresh queueing per WINS tag.
