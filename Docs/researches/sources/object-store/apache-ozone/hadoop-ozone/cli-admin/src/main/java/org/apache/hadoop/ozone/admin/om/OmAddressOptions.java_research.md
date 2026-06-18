<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OmAddressOptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OmAddressOptions.java

Purpose: Provides reusable Picocli mixins for commands that need an OM service ID, OM host, or either. It centralizes option names, deprecated aliases, client creation, and address string rendering.

Important APIs and types: `AbstractMixin`, `rootCommand().getUser()`, `OMAdmin.createOmClient`, nested `OptionalServiceIdMixin`, `MandatoryServiceIdMixin`, `OptionalServiceIdOrHostMixin`, `MandatoryServiceIdOrHostMixin`, `ServiceIdOptions`, and `ServiceIdAndHostOptions`.

Control flow: Service-only mixins call `createOmClient(conf, user, serviceID, null, true)` and require HA-compatible service resolution. Service-or-host mixins call `createOmClient(conf, user, serviceID, host, false)`. Arg groups enforce optional or mandatory presence. Deprecated `-id` and `-host` values are returned if the modern options are absent.

State and persistence behavior: No persistence. Option objects store parsed values for the current invocation. `toString()` renders options back into CLI fragments, used by list-open-files pagination.

Dependencies and integration points: Used by most OM admin subcommands and indirectly by generated next-batch command text. It is coupled to root-command user/config access through `AbstractMixin`.

Risks: `ServiceIdAndHostOptions` extends `ServiceIdOptions`, so rendering can produce both service ID and host when supplied through aliases; host mode later overrides service ID in `OMAdmin`. The rendered option string is not shell-escaped.

Test signals: Exercise optional and mandatory multiplicity, modern and deprecated options, host/service precedence, `newClient()` forceHA flags, and `toString()` output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OmAddressOptions.java -->
