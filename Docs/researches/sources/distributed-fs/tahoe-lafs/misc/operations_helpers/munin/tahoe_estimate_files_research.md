# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_estimate_files

## Purpose

This Munin plugin estimates total files/directories in a grid by sampling storage-index directories from a configured subset of storage servers.

## Important APIs, Types, and Functions

The script uses hard-coded `node_dirs`, sampled two-character `sections`, encoding parameter `N = 10`, and `num_servers = 20`. It counts unique storage index strings and applies a correction based on probability that a file is absent from sampled servers.

## Control Flow

Config mode prints one graph field. Normal mode lists storage share sections under each node dir, builds a set of index strings, computes `chance = N / num_servers`, `no_chance = (1 - chance) ** len(node_dirs)`, extrapolates across all 1024 sections, and prints `files.value`.

## State, Dependencies, Integration, Risks, and Tests

State is local filesystem reads only. Integration is rough operational estimation. Risks include hard-coded production paths, unhandled missing directories, simplistic correction formula, and assumptions about Tahoe share directory fanout and encoding. Tests should build temporary share trees and validate extrapolation for known samples, plus missing sections.
