## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/recon/ReconConfig.java

Purpose: annotated configuration bean for Recon service security settings.

Important APIs/configs: Kerberos principal, Kerberos keytab file, datanode container protocol ACL, getters/setters, and nested `ConfigStrings` constants for the same config keys.

Control flow/state: mutable bean fields populated by config injection. Defaults are empty principal/keytab and wildcard ACL. Dependencies: HDDS config annotations and tags.

Integration points: Recon daemon login, generated default configs, service ACL setup, and consumers using string constants. Risks: wildcard ACL default is permissive; empty Kerberos settings require consumers to handle insecure or disabled auth modes; duplicated key strings in annotations and `ConfigStrings` can drift. Test signals: config binding defaults, getter/setter behavior, generated XML keys, and ACL/Kerberos integration.
