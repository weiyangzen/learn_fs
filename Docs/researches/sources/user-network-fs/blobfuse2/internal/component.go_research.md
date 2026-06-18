## sources/user-network-fs/blobfuse2/internal/component.go

Purpose: Defines the central blobfuse2 component interface and component priority values.

Important APIs: `ComponentPriority` constructors define ordering levels: producer, level one, mid, level two, and consumer. `Component` requires pipeline metadata/config/lifecycle, next-component linkage, directory operations, file operations, flush/release semantics, symlink operations, attribute/setattr operations, block offset retrieval, file-use notification, statfs, committed block list, stage data, and commit data.

State and dependencies: This file has no runtime state except exported priority sentinel `EComponentPriority`. It imports `context`, `syscall`, `common`, and `handlemap`.

Integration points: It is the contract implemented by loopback, xload, libfuse-facing components, storage backends, caches, and exported wrapper aliases. Comments document important expectations such as `ReadDir`/`GetAttr` returning not-exist errors and `CreateFile` returning exists errors.

Risks: Interface breadth means all components must either implement or inherit many methods; neutral defaults can mask missing behavior. Contract comments are not compiler-enforced. Tests are indirect through concrete component suites.
