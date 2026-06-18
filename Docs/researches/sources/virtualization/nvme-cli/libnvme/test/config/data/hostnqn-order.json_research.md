# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/hostnqn-order.json

## Purpose
JSON fixture for host identity precedence/order testing.

## Contents
Defines two host entries with different host NQN/host ID pairs, each containing subsystem `nqn.io-1` and two TCP ports at `192.168.154.144:4420` and `:4421`.

## Relevance
The first host entry acts as the default JSON host identity for `libnvme_host_get_ids()` when command-line/env IDs are absent.
