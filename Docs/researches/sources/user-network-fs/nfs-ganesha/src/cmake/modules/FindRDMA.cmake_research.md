# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRDMA.cmake

## Purpose

`FindRDMA.cmake` discovers the paired libibverbs and librdmacm dependencies needed for RDMA transport support. It accepts a combined `RDMA_PATH_HINT` or component-specific `LIBIBVERBS_PREFIX` and `LIBRDMACM_PREFIX`.

## Important APIs, Types, and Functions

The module exports `RDMA_FOUND`, `RDMA_LIBRARY`, and `RDMA_INCLUDE_DIR`, plus component variables from `libfind_pkg_detect`/`libfind_process` for `IBVERBS` and `RDMACM`.

## Control Flow

It seeds pkg-config include and library directory hints for ibverbs and rdmacm, detects `infiniband/verbs.h` with `ibverbs`, detects `rdma/rdma_cma.h` with `rdmacm`, processes each component, and sets aggregate RDMA variables only if both are found. Final validation uses `FindPackageHandleStandardArgs`.

## State and Persistence Behavior

All state is CMake configure/cache state. Component discoveries may mark include/library options advanced through `LibFindMacros`.

## Dependencies and Integration Points

It depends on `LibFindMacros.cmake`, pkg-config when available, libibverbs, and librdmacm. It integrates with RPC/RDMA transport builds and any target linking RDMA support.

## Risks and Edge Cases

Both component libraries are mandatory for `RDMA_FOUND`; partial installs cannot enable a degraded mode. The aggregate variables are singular names containing lists, which is conventional here but can surprise callers expecting plural variables. Version detection is commented out, so ABI compatibility relies on compile/link failures.

## Test Signals

Configure with system RDMA packages, separate component prefixes, only one component installed, and no RDMA packages. A transport build that includes RDMA headers and links both libraries is the integration test.
