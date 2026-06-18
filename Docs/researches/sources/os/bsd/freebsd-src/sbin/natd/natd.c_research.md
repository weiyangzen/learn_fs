# File Research: sources/os/bsd/freebsd-src/sbin/natd/natd.c

## Summary
Implements FreeBSD `natd`, a divert-socket network address translation daemon built on `libalias`. It supports multiple aliasing instances, dynamic interface address tracking, port/protocol/address redirects, transparent proxy rules, firewall punching, verbose/syslog packet reporting, and graceful shutdown delay.

## Main Responsibilities
- Initializes one or more `struct instance` objects, each with its own `libalias` handle and divert socket configuration.
- Parses command-line and config-file options through a table-driven option system.
- Opens PF_DIVERT sockets for shared or separate inbound/outbound processing, plus optional global divert socket.
- Optionally derives alias address and MTU from an interface, including dynamic refresh through routing socket messages.
- Processes packets from divert sockets, determines direction, applies `LibAliasOut`, `LibAliasIn`, or `LibAliasOutTry`, and reinjects packets.
- Drops ignored incoming packets when configured and logs denied packets.
- Sends ICMP fragmentation-needed messages when aliased packets exceed MTU.
- Supports daemonization, pidfile writing, syslog facilities, SIGHUP module/address refresh, and delayed SIGTERM shutdown.
- Configures libalias modes and redirects: port, protocol, address, LSNAT server pools, proxy rules, Skinny port, and ipfw punch rules.

## Key Functions
- `main()`: lifecycle, socket setup, select loop.
- `DoAliasing()` and `DoGlobal()`: packet receive, aliasing, logging, reinjection.
- `SetAliasAddressFromIfName()`: sysctl route table scan for interface address/MTU.
- `HandleRoutingInfo()`: marks instances for address refresh.
- `ParseArgs()`, `ParseOption()`, `ReadConfigFile()`: option handling.
- `SetupPortRedirect()`, `SetupProtoRedirect()`, `SetupAddressRedirect()`.
- `StrToAddr()`, `StrToPort()`, `StrToPortRange()`, `StrToAddrAndPortRange()`.
- `NewInstance()`: creates or switches named libalias instance.
- `CheckIpfwRulenum()`: validates ipfw punch rule ranges.

## Dependencies And Integration
Uses PF_DIVERT sockets, PF_ROUTE sockets, raw ICMP socket, route-table sysctl, `libalias`, syslog, service/protocol databases, and ipfw default-rule sysctl.

## Research Notes
Multi-instance support is implemented with a global current instance pointer (`mip`) and current libalias handle (`mla`), so parsing and packet dispatch are stateful. Config-file parsing strips comments and trailing whitespace but requires the final line to end with a newline.
