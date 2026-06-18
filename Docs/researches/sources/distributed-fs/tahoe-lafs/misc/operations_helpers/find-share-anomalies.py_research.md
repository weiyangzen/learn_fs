# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/find-share-anomalies.py

## Purpose

This command analyzes `tahoe catalog-shares` outputs from storage servers to find storage indexes with inconsistent CHK/SDMF encodings or multiple SDMF versions.

## Important APIs, Types, and Functions

The script uses dictionaries keyed by storage index. For CHK and SDMF records, each value stores a set of observed encoding/version keys and the original catalog lines.

## Control Flow

It scans every input catalog file, splits each line, records CHK `(si, kN)` encodings, SDMF `(si, kN)` encodings, and SDMF versions. After scanning, it filters keys with more than one encoding or version and prints grouped reports with original lines.

## State, Dependencies, Integration, Risks, and Tests

State is in-memory anomaly maps. Dependencies are exact `catalog-shares` output fields. Integration is storage operations diagnostics. Risks include crashing on blank/malformed lines, ignoring MDMF or newer formats, and tuple shapes that redundantly include `si`. Tests should use small catalog fixtures for normal shares, duplicate encodings, duplicate versions, malformed lines, and mixed CHK/SDMF data.
