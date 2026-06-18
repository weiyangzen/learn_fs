# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/TestOmConfig.java

Purpose: validates `OmConfig` binding from `OzoneConfiguration`, invalid value handling, copying, and field-wise updates.

Important APIs/types/functions: exercises `conf.getObject(OmConfig.class)`, `OmConfig.Keys.SERVER_LIST_MAX_SIZE`, `OmConfig.Keys.USER_MAX_VOLUME`, `copy`, `setFrom`, and getters/setters for filesystem-path, key-name check, max list size, and max user volume count.

Control flow and state: tests create mutable in-memory configurations, set valid and invalid scalar values, and compare resulting objects. Invalid list sizes `-1` and `0` are overridden with defaults, while invalid user max volume throws `IllegalArgumentException`.

Dependencies and integration points: integrates with HDDS typed configuration binding through `MutableConfigurationSource` and `OzoneConfiguration`. These settings affect OM server list response limits and namespace/user behavior.

Risks and test signals: protects against invalid configuration reaching runtime and against shallow/incomplete copying when OM config is propagated or refreshed. Any new mutable `OmConfig` field should be added to `assertConfigEquals`.
