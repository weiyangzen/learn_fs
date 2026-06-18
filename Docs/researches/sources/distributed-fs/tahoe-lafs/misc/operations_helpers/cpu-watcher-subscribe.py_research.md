# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/cpu-watcher-subscribe.py

## Purpose

This Foolscap service subscribes to CPU watcher updates and prints average CPU records as they arrive.

## Important APIs, Types, and Functions

`RICPUWatcherSubscriber` defines remote `averages`. `CPUWatcherSubscriber` is both `service.MultiService` and `Referenceable`; it loads a FURL from a direct `pb://` string, a file, or `watcher.furl` inside a directory, connects via `Tub.connectTo`, requests current averages, subscribes itself, and prints remote updates in `remote_averages`.

## Control Flow

At top level, the subscriber is created from `sys.argv[1]`, started as a service, and the reactor runs indefinitely. On connection it fetches initial data and registers for callbacks; errors go to Twisted logging.

## State, Dependencies, Integration, Risks, and Tests

State is the live Foolscap connection and service tree. Dependencies are Foolscap schemas, Twisted service/reactor/log, and old `zope.interface.implements`. Integration is CPU watcher monitoring. Risks include Python 3 incompatibility from `implements`, no reconnect policy visible here, no argument validation, and no authentication policy beyond the FURL. Tests should use a fake watcher remote reference to check FURL loading, initial call, subscription call, and callback printing.
