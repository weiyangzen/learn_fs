# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java

## Purpose
`TestKeyManagerImpl` is a broad integration/unit hybrid for `KeyManagerImpl`. It starts real SCM/OM test managers but also uses mocked SCM block/container clients to cover key opening, block allocation, directory/file semantics, ACL checks, prefix ACLs, lookup and pipeline refresh, list-status behavior with DB/cache interactions, fake directories, multipart part selection, and previous-snapshot key/dir resolution.

## Important APIs, Types, and Functions
- `setUp()` initializes metadata directories, topology-aware read config, SCM with a mock node manager and network topology, `OmTestManagers`, `KeyManagerImpl`, `PrefixManager`, write/rpc clients, and mock SCM clients. It also configures safe-mode block allocation failures and creates the base volume.
- `init()` and `cleanupTest()` create buckets before each test and remove them via OFS `FileSystem` paths afterward.
- SCM switching helpers `mockContainerClient()` and `mockBlockClient()` replace internal `scmClient` fields on `keyManager` and `om`.
- Directory/file tests cover `createDirectory`, create-file overwrite/recursive rules, file under nonexistent parent, directory under file, root directory behavior, lookup file, and `getFileStatus`.
- ACL tests cover file, directory, nonexistent key access, prefix ACL add/set/remove/get, invalid prefix validation, and longest-prefix lookup.
- Listing tests exercise table cache merging, recursive and non-recursive status, deleted cache entries, pagination, filesystem-path config toggles, and fake directory discovery.
- Pipeline and version tests cover topology-aware closest-node sorting, latest-only versus all-version location behavior, refresh batching by container ID, and exception mapping to `SCM_GET_PIPELINE_EXCEPTION`.
- Multipart tests select all parts with part number zero, a specific part, or no locations for a missing part.
- Previous-snapshot tests verify object-ID based rename-table lookup for keys across all bucket layouts and FSO directory info.

## Control Flow
The setup path constructs a realistic OM/SCM environment and then mutates internals to simulate SCM failures or container-pipeline lookups. Many tests create `OmKeyArgs`, call write-client methods (`openKey`, `createFile`, `commitKey`, `createDirectory`, ACL APIs), and assert `KeyManagerImpl` read-side behavior. Metadata-heavy tests insert entries directly through `OMRequestTestUtils` into DB tables or table cache, then call `listStatus` and validate counts, sorting, deleted-entry filtering, pagination, and directory/file classification.

## State and Persistence Behavior
The file exercises multiple state layers: OM volume/bucket/key/open-key tables, key table cache entries including delete markers, prefix ACL metadata, directory marker/fake directory semantics, versioned bucket key-location versions, snapshot renamed table mappings, SCM container-to-pipeline metadata, Ratis/standalone replication configs, and filesystem-path configuration flags. Cleanup deletes per-test buckets but static managers persist across tests.

## Dependencies and Integration Points
Major integrations include `OmTestManagers`, `StorageContainerManager`, `ScmClient`, SCM block/container protocols, Hadoop `FileSystem`, `OMRequestTestUtils`, `PrefixManager`, `OzoneManagerProtocol`, Ozone ACL/request context types, `InMemoryTestTable`, Mockito, network topology classes, pipeline manager, and bucket layout-specific metadata key builders.

## Risks and Test Signals
Risks include static cross-test state, direct internal field mutation through whitebox utilities, cache delete-marker cleanup requirements, assumptions about network topology node ordering, and config toggles not restored per test. Strong signals include exact OM exception result codes, block count for multi-block opens, created parent directory rows, access checks avoiding SCM pipeline calls, ACL merge/remove behavior, longest-prefix result positions, latest-version location counts, list-status counts and pagination sets, fake-directory positives/negatives across buckets, SCM refresh call counts, exception result mapping, multipart part filtering, and previous-snapshot lookup results through rename tables.
