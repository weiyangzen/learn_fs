
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/ObjectParser.java

Purpose: Parses ACL object paths into volume, bucket, and key/prefix components according to requested object type.

Important APIs and types: Uses `OzoneObj.ObjectType`, `OZONE_URI_DELIMITER`, `StringUtils.split(path, delimiter, 3)`, and `OMException.ResultCodes.INVALID_PATH_IN_ACL_REQUEST`.

Control flow: Constructor rejects null paths, splits into at most three tokens, accepts exactly one token for volumes, two for buckets, and three for keys or prefixes; otherwise it throws `OMException`. Getters expose parsed components.

State and persistence behavior: Stores parsed fields in the parser instance only; no persistence.

Dependencies and integration points: Used by ACL request handling to translate `OzoneObj.getPath()` into OM metadata names.

Risks: Empty/multiple-delimiter paths are normalized by `StringUtils.split`, so callers must understand that empty tokens are discarded. Tests should cover legal volume/bucket/key/prefix paths and malformed/empty paths.
