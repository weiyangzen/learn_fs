## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/core-site.xml

**Purpose:** Provides an empty Hadoop-style `core-site.xml` template for site-specific configuration overrides in the Ozone/HDDS distribution.

**Important APIs/types/functions:** The XML declares the Hadoop configuration stylesheet and an empty `<configuration>` root. It contains no `<property>` entries.

**Control flow:** Runtime/configuration loading only. Hadoop/Ozone configuration loaders can include this file and merge any site-specific properties if operators add them.

**State and persistence:** Persistent configuration template. As checked in, it contributes no runtime key/value state.

**Dependencies and integration points:** Used by Hadoop `Configuration`/Ozone configuration loading conventions and distribution packaging. Pairs with other conf files under `common/src/main/conf`.

**Risks:** Because it is empty, deployments must supply meaningful overrides elsewhere. Editing this template directly can affect packaged defaults globally.

**Test signals:** XML well-formedness and packaging are the primary signals; no direct test in this subset.
