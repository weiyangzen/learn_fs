# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneFsUtils.java

Purpose: tests filesystem-style path validation and hsync feature gating in `OzoneFSUtils`.

Important APIs/types/functions: exercises `OzoneFSUtils.isValidName`, `canEnableHsync`, and `isValidKeyPath`.

Control flow and state: name tests accept absolute `/a/b` style names and reject relative paths, dot components, colon components, and double slashes. `canEnableHsync` is parameterized across server/client hbase enhancement config and `ozone.fs.hsync.enabled`; hsync is allowed only when both relevant enhancement and fs hsync flags are true. Key path validation returns valid relative paths, handles empty path based on `throwOnEmpty`, and throws `OMException` for invalid patterns.

Dependencies and integration points: uses `OzoneConfiguration`, `OzoneConfigKeys`, and `OMException`. These utilities guard OM key namespace operations and HBase-oriented hsync features.

Risks and test signals: catches path traversal and malformed key names, client/server config key confusion, and accidental hsync enablement when prerequisites are disabled. Coverage includes trailing slash as a valid key path.
