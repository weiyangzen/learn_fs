## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/StoreTypeOption.java

Purpose: reusable ACL store-type option and converter.

Important APIs and control flow: option `--store`/`-s` defaults to `OZONE` and is converted by this class to `OzoneObj.StoreType`. `convert` returns `OZONE` for null and otherwise uses enum `valueOf`.

State and dependencies: parse-time state only. Depends on picocli and `OzoneObj.StoreType`.

Risks and test signals: enum conversion is case-sensitive, so invalid/lowercase values fail through picocli. Consumed by `AclHandler` when building `OzoneObj`.
