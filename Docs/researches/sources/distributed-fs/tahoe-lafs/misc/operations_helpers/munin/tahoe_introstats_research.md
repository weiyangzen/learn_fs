# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_introstats

## Purpose

This Munin plugin graphs introducer announcement/subscription counts for storage service participants.

## Important APIs, Types, and Functions

It reads JSON from env `url` and expects `announcement_summary`, `announcement_distinct_hosts`, and `subscription_summary`, each with a `storage` key.

## Control Flow

Config mode prints three series: storage servers, distinct storage hosts, and clients. Normal mode fetches JSON and prints values for those keys.

## State, Dependencies, Integration, Risks, and Tests

No persistent state. Integration is Tahoe introducer stats endpoint monitoring. Risks include schema KeyError, no timeout, and only storage service support. Tests should use fixture JSON for normal output and missing-key behavior.
