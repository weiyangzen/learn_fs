# sources/distributed-fs/tahoe-lafs/misc/incident-gatherer/classify_tahoe.py

## Purpose

This incident-gatherer classifier maps Tahoe Foolscap incident trigger dictionaries to stable category strings for known failure patterns.

## Important APIs, Types, and Functions

`umidmap` maps selected UMIDs to categories. `classify_incident(trigger)` checks `message`, `format`, `umid`, `facility`, `isError`, and `failure` fields, then returns a category or `None`.

## Control Flow

UMID matches win first. Message regexes classify mutable publish surprise shares, mutable query failures by source path and error type, mutable retrieve failures, bad private keys, and introducer connection loss/failure. Unrecognized triggers fall through to `None`.

## State, Dependencies, Integration, Risks, and Tests

State is static map data. Dependency is `re`. Integration is Foolscap incident classification, aided by `make_umid` and `check-umids.py`. Risks include brittle substring/traceback matching, stale UMIDs, conflating multiple cut-and-paste error sites, and missing structured fields. Tests should feed representative trigger dictionaries for every branch, including unknown mutable query locations and introducer failures.
