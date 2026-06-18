# File Research: sources/virtualization/qemu/hw/virtio/vhost-iova-tree.c

## Purpose
Implements `VhostIOVATree`, a helper for allocating and translating IOVA ranges used by vhost software live migration and shadow virtqueues.

## Main Structure
- `iova_first` / `iova_last`: allocatable device IOVA range, with low address zero avoided.
- `iova_taddr_map`: maps IOVA to translated host virtual addresses.
- `iova_map`: tracks allocated IOVA ranges.
- `gpa_iova_map`: maps guest physical addresses to IOVAs.

## Key Behavior
- Creates separate IOVA and GPA-backed interval trees.
- Avoids address zero by starting at at least one real host page.
- Finds IOVA mappings by translated host address or GPA.
- Allocates a new IOVA range, validates overflow and permissions, inserts into allocation tree, then inserts into the translated-address tree.
- Provides separate allocation/removal paths for HVA-backed and GPA-backed mappings.

## Filesystem/Storage Relevance
This supports address translation for vhost-vDPA/shadow virtqueue paths, where guest buffers must be represented as device-visible IOVA ranges during migration or mediated data path operation.
