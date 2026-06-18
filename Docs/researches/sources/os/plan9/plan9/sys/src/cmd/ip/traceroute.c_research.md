# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/traceroute.c

## Purpose
Implements `traceroute` using Plan 9 network conversation files. It probes successive TTL values and reports hop address, low/average/high round-trip time in microseconds, and optional reverse DNS names.

## Main Behavior
Parses dial strings into netdir/protocol/remote components. Defaults to `/net`, protocol `tcp`, and remote service `32767` when no service is present. `csquery()` asks `/net/cs` to resolve the dial string, falling back to direct numeric dialing when no connection server is available.

## Probe Types
`call()` opens the protocol clone, opens the data file, sets TTL through the control file, and dispatches to protocol-specific probes:
- TCP/IL: writes a `connect` request and relies on connection errors.
- UDP: connects to an unlikely port and sends data until timeout or network error.
- ICMP: sends ICMPv4 echo requests and validates echo replies with a magic sequence and payload.

## Output
For each TTL, runs multiple tries, aggregates timing, prints hop info, and can print histograms with `-h`. `-n` suppresses reverse DNS. `-a` sets tries, `-t` starting TTL, and `-x` net mount point.

## Dependencies
Uses `/net`, `/net/cs`, DNS through `dnsquery`, Plan 9 alarms/notes, and `icmp.h`.
