# File Research: sources/local-fs/ocfs2-tools/documentation/samples/cluster.conf

## Role

This is a sample OCFS2/O2CB cluster configuration.

## Contents

It defines a cluster named `webcluster` with global heartbeat mode and three nodes:

- `node7` at `192.168.0.107`, node number 7, port 7777.
- `node6` at `192.168.0.106`, node number 6, port 7777.
- `node10` at `192.168.0.110`, node number 10, port 7777.

It also defines three heartbeat regions for the cluster by UUID-like region identifiers.

## Usage

The file is installed as a Debian example by `debian/rules` and included in distribution archives.
