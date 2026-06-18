# sources/user-network-fs/nfs-ganesha/src/include/conf_url_rados.h

## Purpose
`conf_url_rados.h` is the build-gated public interface for the RADOS-backed configuration URL provider. It only exposes declarations when `RADOS_URLS` is enabled in generated `config.h`.

## Important APIs, Types, And Functions
When enabled, it includes `librados.h` and declares `gsh_rados_url_setup_watch`, `gsh_rados_url_shutdown_watch`, and `register_service_to_ceph`. These functions bridge generic config URL handling to Ceph/RADOS service discovery and watch behavior.

## Control Flow
The generic `conf_url.c` code dynamically loads the RADOS URL module and resolves setup/shutdown watch callbacks. Provider initialization is expected to happen from the RADOS module package init, which registers a `gsh_url_provider` with the generic URL layer.

## State And Persistence
The header itself has no state. Runtime state is in the RADOS provider and may include librados cluster/ioctx handles, watches, object contents, and service registration data in Ceph. That state persists externally in the Ceph cluster as defined by the provider.

## Dependencies And Integration Points
It depends on generated feature macro `RADOS_URLS`, `gsh_list.h`, `stdbool.h`, and `<rados/librados.h>`. It integrates with `conf_url.h`, the RADOS URL shared library, and any cluster service registration path that calls `register_service_to_ceph`.

## Risks
All declarations disappear when `RADOS_URLS` is unset, so callers must be feature-gated or use the generic no-op wrappers in `conf_url.h`. Linking directly against these functions in a non-RADOS build will fail. The provider involves external Ceph credentials, network state, and watch lifetimes, so shutdown ordering is important.

## Test Signals
Build matrix coverage should include both `RADOS_URLS=ON` and `OFF`. Runtime tests need missing librados/backend handling, successful provider registration, watch setup/shutdown, Ceph service registration, URL fetch of existing and missing objects, and shutdown after failed partial initialization.
