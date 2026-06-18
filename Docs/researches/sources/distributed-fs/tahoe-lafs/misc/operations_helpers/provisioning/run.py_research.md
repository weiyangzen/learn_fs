# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/run.py

## Purpose

This launcher starts a local Nevow web app exposing the provisioning and reliability calculators.

## Important APIs, Types, and Functions

`Root` is a Nevow `rend.Page` with links and child resources `child_reliability` and `child_provisioning`. `run(portnum)` creates the root, serves `tahoe.css`, starts a Twisted `strports` TCP service, opens a browser after one second, and runs the reactor.

## Control Flow

When executed directly, it defaults to port `8070` unless an argument overrides it, then calls `run`. The web server remains active until the reactor stops externally.

## State, Dependencies, Integration, Risks, and Tests

State is the live Twisted service and browser side effect. Dependencies are Twisted, Nevow, local calculator modules, and `webbrowser`. Risks include no error handling for occupied ports, automatic browser launch in noninteractive environments, and import failure if NumPy/Nevow are unavailable. Tests should instantiate `Root`, verify child resources, and exercise `run` with a fake reactor/service/browser.
