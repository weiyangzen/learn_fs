# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/BaseGenerator.java

Purpose: shared base for offline Ozone container metadata/data generators.

Important APIs/types/functions: `BaseGenerator extends BaseFreonGenerator implements Callable<Void>, VaporSubcommand`; options `--user`, `--key-size`, `--size`, and `--from`; getters `getUserId`, `getKeysPerContainer`, `getContainerIdOffset`, `getContainerSize`, and `getKeySize`.

Control flow: subclasses call getters during generation. `getContainerSize` uses explicit `--size` when supplied, otherwise reads `ozone.scm.container.size` from `ConfigurationSource` with SCM defaults. `getKeysPerContainer` integer-divides container size by key size.

State/persistence: no direct writes. It centralizes generation parameters, including a static user id shared by subclass commands in the JVM.

Dependencies/integration: Ozone Freon base class, HDDS configuration APIs, SCM container-size config, picocli options, and `VaporSubcommand`.

Risks: `userId` is static, so multiple generator instances in one JVM could share/overwrite it. `getKeysPerContainer` truncates remainders and can return zero if key size exceeds container size. No validation prevents zero/negative key sizes or offsets.

Test signals: no direct test. Subclass tests should cover default container-size resolution and key-count boundary cases.
