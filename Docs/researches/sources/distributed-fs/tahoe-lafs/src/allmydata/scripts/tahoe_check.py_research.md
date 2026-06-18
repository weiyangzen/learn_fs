# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_check.py

## Purpose
Implements `tahoe check` and `tahoe deep-check`, including optional verification, repair, lease renewal, raw JSON output, and human-readable summaries of corrupt shares and repair results.

## APIs, Types, And Control Flow
`check_location` resolves an alias/path, POSTs `?t=check&output=JSON` with selected flags, and formats either normal check results or pre/post repair summaries. `check` applies it to all requested locations or the default root. Deep checking uses `DeepCheckStreamer`, which POSTs `?t=stream-deep-check`, reads the response stream in chunks, and feeds lines into `DeepCheckOutput` or `DeepCheckAndRepairOutput`. Those `LineOnlyReceiver` subclasses count checked objects, healthy/unhealthy files, repair attempts, and corrupt shares; verbose mode prints one line per object.

## State, Persistence, And Integration
No local files are written. Remote state may change when `--repair` repairs shares or `--add-lease` renews leases. Integrates with the gateway web API, shared alias/path escaping, blocking HTTP client, Twisted line parsing, JSON, and output encoding helpers.

## Risks And Test Signals
Risks include assuming JSON response shapes, reading deep-check streams synchronously, rc handling when a streamed `ERROR:` line appears, and remote mutation when repair or lease options are set. LIT files are special-cased because they lack some fields. Test signals are `allmydata/test/cli/test_check.py`, deep-check/checker tests, repairer tests, and web check-results tests.
