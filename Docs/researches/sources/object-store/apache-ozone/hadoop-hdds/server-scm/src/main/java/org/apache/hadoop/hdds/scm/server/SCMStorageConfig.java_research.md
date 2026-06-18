# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStorageConfig.java

Purpose: `SCMStorageConfig` specializes the common Ozone `Storage` abstraction for SCM. It locates SCM's storage directory, sets the initial HDDS layout version, and manages SCM-specific VERSION-file properties such as SCM ID, HA status, primary SCM node ID, and SCM certificate serial ID.

Important APIs and types: Constructors call `Storage(NodeType.SCM, ServerUtils.getScmDbDir(conf), STORAGE_DIR, initLayoutVersion)`. Public methods include `setScmId`, `getScmId`, `setSCMHAFlag`, `isSCMHAEnabled`, `setScmCertSerialId`, `getScmCertSerialId`, `setPrimaryScmNodeId`, `getPrimaryScmNodeId`, and `checkPrimarySCMIdInitialized`. `TESTING_INIT_LAYOUT_VERSION_KEY` lets tests force an initial layout version.

Control flow: During SCM init or bootstrap, callers construct this object, set cluster and SCM-specific properties, then call `initialize` or `forceInitialize` inherited from `Storage`. During normal startup, SCM reads the storage state and these properties to decide whether startup, Ratis migration, HA bootstrap, or security initialization is allowed. `getNodeProperties` generates a random SCM ID only if one has not already been provided.

State and persistence behavior: The persistent state is the SCM VERSION file under the SCM DB storage directory. `SCM_ID`, `SCM_HA`, `SCM_CERT_SERIAL_ID`, and `PRIMARY_SCM_NODE_ID` are stored as properties. `setScmId` refuses to mutate an already initialized storage config, while the other setters update the in-memory property set for later force-initialization or persistence. `setSCMHAFlag` is one-way in practice because it does not overwrite an already true HA flag.

Dependencies and integration points: It is consumed heavily by `StorageContainerManager`, `SCMHANodeDetails`, HA/Ratis initialization, SCM security bootstrapping, certificate clients, upgrade finalization, and tests that need a formatted SCM directory. It depends on `HDDSLayoutVersionManager.maxLayoutVersion` and `ServerUtils.getScmDbDir`.

Risks: Accidentally using `forceInitialize` after changing properties can rewrite important VERSION values, so callers must preserve cluster ID and SCM ID carefully. `Boolean.valueOf(null)` makes missing `SCM_HA` read as false, which supports upgrade paths but can mask incomplete initialization. `setSCMHAFlag(false)` cannot clear a true flag. Random SCM ID generation in `getNodeProperties` means tests that need deterministic IDs must set them explicitly before initialize.

Test signals: Useful assertions cover uninitialized vs initialized `setScmId`, default random SCM ID creation, HA flag one-way behavior, certificate serial persistence, primary SCM ID checks, forced test layout version, and SCM DB directory fallback behavior in `ServerUtils`.
