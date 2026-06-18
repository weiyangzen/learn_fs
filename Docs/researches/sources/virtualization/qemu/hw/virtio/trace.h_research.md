# File Research: sources/virtualization/qemu/hw/virtio/trace.h

## Purpose
Includes the generated trace header for the `hw/virtio` subsystem.

## Key Behavior
- Single include of `trace/trace-hw_virtio.h`.
- Allows virtio source files in this directory to use generated tracepoints.

## Filesystem/Storage Relevance
Tracepoints are used in vhost-user and related device paths to debug memory mapping, migration, IOTLB, and notifier behavior.
