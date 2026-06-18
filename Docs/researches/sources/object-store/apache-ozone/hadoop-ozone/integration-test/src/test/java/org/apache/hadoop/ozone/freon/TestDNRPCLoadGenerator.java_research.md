# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDNRPCLoadGenerator.java

Purpose: Non-HA Freon integration test for `DNRPCLoadGenerator`, validating direct datanode RPC load generation against a real allocated container in read/write and Ratis/non-Ratis modes.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `StorageContainerLocationProtocolClientSideTranslatorPB.allocateContainer`, `XceiverClientCreator`, `ContainerProtocolCalls.createContainer`, `DNRPCLoadGenerator`, and picocli `CommandLine`. Parameter provider covers `(readOnly, ratis)` booleans.

Control flow: `init` allocates a standalone replication-one container through SCM, opens an xceiver client to the pipeline, and creates the container on the datanode. The parameterized test builds the generator with cluster config, supplies container ID, five clients, ten threads/operations via `-t 10`, and optional `--read-only` and `--ratis` flags, then asserts command exit code zero.

State and persistence behavior: The allocated container is persisted in the mini cluster during setup. Load generator calls perform direct DN RPCs that may read or write container data depending on flags. No explicit post-run container content validation is performed beyond exit code.

Dependencies and integration points: Exercises SCM container allocation, xceiver client factory, datanode container creation, Freon CLI parsing, and direct DN RPC load code.

Risks: Exit-code-only validation may miss partial operation failures if the generator swallows them. Shared setup container is reused across parameter cases. Load generation can be timing-sensitive under constrained CI.

Test signals: `cmd.execute` must return `0` for all four read-only/Ratis combinations.
