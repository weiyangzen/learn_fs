# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_files

## Purpose

This Munin plugin counts share files under one or more Tahoe node storage directories.

## Important APIs, Types, and Functions

It discovers node directories from environment variables named `basedir_NODE`, emits one Munin series per node, and walks `storage/shares`, excluding the top-level `incoming` directory.

## Control Flow

The script builds sorted `(nodename, basedir)` pairs. Config mode prints labels/draw styles. Normal mode walks each storage root and prints the count of filenames.

## State, Dependencies, Integration, Risks, and Tests

State is local filesystem traversal. Integration is per-node Munin monitoring. Risks include field names taken directly from env suffixes, expensive full tree walks, symlink traversal behavior inherited from `os.walk`, and no handling for missing roots. Tests should use temporary share trees with `incoming`, multiple nodes, and empty/missing directories.
