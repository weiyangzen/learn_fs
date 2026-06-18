# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMStarterInterface.java

Purpose: This small interface abstracts the operations needed by the SCM command-line starter so production startup code can be replaced in tests. It is the injection seam between `StorageContainerManagerStarter` and the static creation, init, bootstrap, and cluster-ID generation methods on SCM.

Important APIs and types: The interface declares `start(OzoneConfiguration)`, `init(OzoneConfiguration, String)`, `bootStrap(OzoneConfiguration)`, and `generateClusterId()`. It depends only on `OzoneConfiguration`, `IOException`, and Hadoop `AuthenticationException`.

Control flow: `StorageContainerManagerStarter` calls one of these methods from the default command path or from the `--init`, `--bootstrap`, and `--genclusterid` picocli subcommands. The nested production helper implements them by delegating to `StorageContainerManager.createSCM`, `StorageContainerManager.scmInit`, `StorageContainerManager.scmBootstrap`, and `StorageInfo.newClusterID`.

State and persistence behavior: The interface owns no state. Its implementations decide whether SCM storage VERSION files are created, cluster IDs are generated, bootstrap metadata is written, or an SCM daemon is started.

Dependencies and integration points: It integrates the CLI layer with SCM initialization and start lifecycle while allowing unit tests to verify command behavior without launching an SCM or mutating real storage.

Risks: The method names are part of CLI testability rather than a general service API. `bootStrap` preserves a nonstandard capital S spelling, so callers and implementations must match it exactly. Implementations must preserve the boolean result contract used by the CLI to throw `IOException` on failed init/bootstrap.

Test signals: Tests should inject a fake receiver and assert the CLI passes the parsed `OzoneConfiguration` and optional cluster ID, propagates exceptions, and throws when `init` or `bootStrap` returns false.
