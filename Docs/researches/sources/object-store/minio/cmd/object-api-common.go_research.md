# sources/object-store/minio/cmd/object-api-common.go

This file contains shared object-layer constants, the global object API pointer and mutex, storage initialization options, and the factory that chooses local or remote storage implementations for an endpoint.

Important constants include legacy and current erasure block sizes, bucket metadata prefix, deleted bucket prefix, and the empty-object ETag. `globalObjLayerMutex` protects updates to `globalObjectAPI`, which is the process-wide object layer accessed by helper functions elsewhere. `storageOpts` carries `cleanUp` and `healthCheck` options into disk construction. `newStorageAPI` checks `Endpoint.IsLocal`: local endpoints are opened with `newXLStorage`, wrapped in `newXLStorageDiskIDCheck`, and respect cleanup and health-check settings; remote endpoints are represented by `newStorageRESTClient` using the current global grid.

State is foundational runtime state. It does not persist data itself, but it selects components that read and write erasure data, metadata, and remote disk RPCs. Integration points include server bootstrap, erasure-set construction, storage health checks, bucket metadata paths, MRF storage persistence, and any object-layer code that reads `globalObjectAPI`.

Risks: initialization errors for local storage propagate directly and can stop disk setup. Remote storage depends on `globalGrid.Load()` being initialized. The global object layer must be updated under its mutex elsewhere; misuse can race. No direct tests appear here, so coverage comes from bootstrap and object-layer integration tests.
