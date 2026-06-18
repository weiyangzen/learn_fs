# sources/object-store/minio/cmd/veeam-sos-api.go

Implements Veeam SOSAPI virtual objects `.system.../system.xml` and `.system.../capacity.xml`. `systemInfo`, `capacityInfo`, and `apiEndpoints` model XML responses. `isVeeamSOSAPIObject` recognizes virtual object names, `isVeeamClient` checks the request User-Agent, and `veeamSOSAPIGetObject` synthesizes XML plus object metadata and range support.

`system.xml` reports protocol version, MinIO release model name, capacity capability, and 4096 KB block-size recommendation. `capacity.xml` reads bucket quota and usage; hard quota is used when configured, otherwise usable backend capacity is computed from storage info. These objects are not persisted.

Risks include expensive/stale capacity reporting, negative available capacity if usage exceeds quota, User-Agent substring fragility, and untested XML/range behavior. The environment variable `_MINIO_VEEAM_FORCE_SC` feeds storage-class filtering elsewhere.
