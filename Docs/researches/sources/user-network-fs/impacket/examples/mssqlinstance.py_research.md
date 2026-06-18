# sources/user-network-fs/impacket/examples/mssqlinstance.py

## Purpose

`mssqlinstance.py` queries the SQL Server Browser service using Impacket's MC-SQLR support and prints MSSQL instance metadata advertised by a target host.

## Important APIs, Types, and Functions

The script is CLI-only. It constructs `tds.MSSQL(options.host)`, calls `getInstances(timeout)`, and prints either `No MSSQL Instances found` or each returned instance dictionary as `key:value` lines with an instance index in the logs.

## Control Flow

The CLI accepts host, timeout, debug, and timestamp flags. After logging initialization, it sends the instance discovery request through `MSSQL.getInstances()`. The response is treated as a list of dictionaries and printed in returned key order.

## State and Persistence Behavior

No persistence is used. The script sends a discovery request and writes stdout/log output only.

## Dependencies and Integration Points

It depends on Impacket `tds.MSSQL` and the example logger. It integrates with SQL Server Browser / MC-SQLR discovery, normally over UDP 1434 as implemented by Impacket.

## Risks and Edge Cases

There is no exception wrapper around discovery, so network or parsing failures can terminate with a traceback depending on logging/debug context. Timeout is parsed as an integer only at call time. Returned instance dictionaries are printed without stable key sorting, which can vary by parser behavior. Firewalls often block SQL Browser discovery, producing empty results even when SQL Server is reachable on a fixed port.

## Test Signals

Tests should mock `getInstances()` for empty, single-instance, multi-instance, timeout, and malformed-return cases. Integration tests should query hosts with default and named SQL instances, blocked UDP discovery, and custom timeout values.
