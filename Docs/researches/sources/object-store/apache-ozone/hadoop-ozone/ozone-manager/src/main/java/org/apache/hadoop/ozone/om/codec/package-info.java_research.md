# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.om.codec` as containing byte-array encoders/decoders and OM DB definitions.

Important APIs and types: It exports no runtime type directly. Key package classes are `OMDBDefinition` and `TokenIdentifierCodec`.

Control flow: No executable control flow is present.

State and persistence behavior: No state is held here. The package's concrete classes define persistent OM DB encodings.

Dependencies and integration points: JavaDoc and package ownership only; runtime integration belongs to the package classes.

Risks and test signals: The only risk is documentation drift if codec responsibilities move. No direct tests are needed beyond package class tests.
