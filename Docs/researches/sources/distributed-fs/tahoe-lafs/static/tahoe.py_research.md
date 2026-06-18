# sources/distributed-fs/tahoe-lafs/static/tahoe.py

## Purpose
This script is an executable PyInstaller/static-entry helper for Tahoe-LAFS. It primes dependency discovery and then runs Tahoe's normal script runner.

## Important APIs, Types, and Functions
There are no local functions. The script imports `allmydata`, `Decimal`, `xml.dom.minidom`, `allmydata.web`, and `allmydata.scripts.runner`, then calls `runner.run()`.

## Control Flow
Importing `allmydata` first suppresses deprecation warnings according to the comment. Several otherwise-unused imports are deliberately referenced as bare expressions so pyflakes considers them used and PyInstaller sees them. Finally, control transfers to Tahoe's CLI runner.

## State and Persistence
No local state is persisted. Runtime effects are whatever `runner.run()` performs for the invoked Tahoe command.

## Dependencies and Integration Points
Integrates with PyInstaller packaging, Tahoe's package import side effects, web package dependencies, standard `decimal` and `xml.dom.minidom`, and `allmydata.scripts.runner`.

## Risks and Test Signals
Because this is an entry script, failures are import-time failures. Packaging tests should verify PyInstaller includes the hinted modules and that executing the bundled script reaches `runner.run()`. Unit tests can monkeypatch `runner.run` if this file is imported directly.
