## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclHandler.java

Purpose: abstract base class for shell ACL commands across volumes, buckets, keys, and prefixes.

Important APIs and control flow: defines shared command names/descriptions for add/get/remove/set ACL commands. Mixes in `StoreTypeOption`, converts the current `OzoneAddress` to an `OzoneObj`, and delegates to subclass `execute(OzoneClient, OzoneObj)`.

State and dependencies: no persistence; carries parsed store type. Depends on `Handler`, `OzoneAddress.toOzoneObj`, and Ozone ACL object model.

Risks and test signals: address validation is supplied by concrete URI mixins; wrong resource type/store type would direct ACL operations to the wrong object. Bucket ACL handlers in this subset extend it.
