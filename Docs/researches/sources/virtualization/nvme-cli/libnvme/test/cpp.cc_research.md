# File Research: sources/virtualization/nvme-cli/libnvme/test/cpp.cc

## Purpose
C++ compile/use smoke test for libnvme public headers.

## Behavior
Creates a global context, scans topology while tolerating missing/inaccessible sysfs, traverses hosts/subsystems/controllers/namespaces/paths with public macros, and prints selected attributes with C++ iostreams.

## Relevance
Ensures libnvme headers and traversal APIs are usable from C++ translation units.
