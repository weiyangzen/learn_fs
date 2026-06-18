# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/pom.xml

Purpose: This Maven module defines `ozone-cli-repair`, the jar containing advanced offline/repair tools for Ozone.

Important APIs and types: It inherits from the root Ozone parent, packages a jar, sets `classpath.skip=false`, and depends on Guava, commons-io/lang3/codec, picocli, Jakarta annotations, Hadoop common, HDDS CLI/config/container/SCM/RocksDB artifacts, Ozone debug/shell/client/common/interface/manager artifacts, Ratis artifacts, RocksDB JNI, SLF4J, and metainf-services. Test dependencies include HDDS test jars and utilities.

Control flow and state: Build-time configuration includes SpotBugs with the module exclude file, compiler annotation processors for metainf-services and picocli native-image config generation, and an enforcer override banning selected annotation imports.

Dependencies and integration points: The module packages service-loaded repair subcommands such as datanode schema upgrade and transaction info repair. Runtime dependencies include RocksDB and checkpoint differ support needed by offline DB operations.

Risks: This module has a broad dependency surface and touches offline persistent state, so dependency version mismatches can be high impact. Annotation processor configuration must stay aligned with service registration. Banned import overrides need to remain intentional.

Test signals: Build should compile annotation-generated service metadata, run SpotBugs with the exclude file, enforce banned imports, and execute repair CLI tests that exercise RocksDB/container dependencies.
