# sources/distributed-fs/tahoe-lafs/misc/coding_tools/check-umids.py

## Purpose

This Python 3 checker ensures Foolscap/Tahoe `umid=` logging identifiers are unique across Python source files.

## Important APIs, Types, and Functions

The script walks supplied roots, scans `.py` files, skips lines without the substring `umid`, and extracts IDs with regex `umid=["']([^"']+)["']`. It stores first-use locations in `umids`.

## Control Flow

Every duplicate prints the duplicate location and first-use location and flips `ok` false. At the end, it prints either an all-clear message or a duplicate summary and exits `1`.

## State, Dependencies, Integration, Risks, and Tests

State is the in-memory `umids` dict. Integration is CI linting for incident classification maintainability. Risks include matching comments/strings, missing whitespace around `=`, and not validating ID length/charset. Tests should include unique IDs, duplicates, commented examples, alternate quoting, and spacing variants.
