# sources/user-network-fs/samba/source3/utils/net_witness.c

## Purpose
Implements cluster-only `net witness` diagnostics and controls for SMB Witness registrations: list, client move, share move, force unregister, and forced AsyncNotify response.

## Important APIs, Types, and Functions
`net_witness_open_registration_db()` opens `rpcd_witness_registration.tdb` read-only. The scan framework uses regex filters and action callbacks in `struct net_witness_scan_registrations_action_state`. `net_witness_scan_registrations_parser()` NDR-decodes registrations, skips dead server IDs, filters, processes, and dumps text/JSON. Update paths build `rpcd_witness_registration_updateB` and send it with `messaging_send()`.

## Control Flow
`net_witness()` dispatches five subcommands, all requiring `clustering=yes`. Scanner setup initializes filters/JSON, then does a direct registration lookup or full DB traversal. List is no-op processing. Move commands require explicit selection or apply-all, validate new IP/node options, choose IPv4/IPv6/node update types, and message matching servers. Share move skips registrations without share names. Force unregister and force response send special update types; force response optionally parses JSON into `witness_notifyResponse`.

## State and Persistence
The tool reads the registration DB but does not write it directly. It sends internal messages to owning registration server processes, which may mutate witness state or complete pending notifications.

## Dependencies and Integration Points
Depends on clustered Samba, messaging, server ID liveness, dbwrap/TDB, generated Witness/RPCD NDR, POSIX regex, loadparm clustering, and optional Jansson JSON helpers.

## Risks
Broad filters or apply-all can disrupt many clients. Forced responses are developer/test tools and can drive unusual client behavior. JSON support is compile-time optional. Messaging failures leave selected registrations unchanged.

## Test Signals
Cover clustering-disabled rejection, direct/traverse scans, invalid regex, filter AND behavior, dead server skip, text/JSON output, selection validation, apply-all mutual exclusion, IPv4/IPv6/node/all move variants, share-name filtering, messaging failure, forced-response JSON schemas, and no-Jansson builds.
