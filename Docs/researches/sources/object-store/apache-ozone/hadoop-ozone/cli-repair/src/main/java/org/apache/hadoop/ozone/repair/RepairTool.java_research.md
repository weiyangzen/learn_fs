# sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/RepairTool.java

Purpose: `RepairTool` is the base class for actionable repair commands, providing dry-run formatting, force handling, offline service checks, user confirmation, and stdout/stderr helpers.

Important APIs and types: It extends `AbstractSubcommand` and implements `Callable<Void>`. Subclasses implement `execute` and may override `serviceToBeOffline`. Options are `--force` and `--dry-run`. It defines `Component` enum values `DATANODE`, `OM`, and `SCM`.

Control flow: `call` determines the service requirement, prompts for user confirmation for non-dry-run offline tools, calls `isServiceStateOK`, and runs subclass `execute` only when checks pass. Service state is inferred from environment variables `OZONE_<SERVICE>_RUNNING` and `OZONE_<SERVICE>_PID`; `--force` bypasses a positive running check.

State and persistence behavior: It stores a lazily created `Scanner` for confirmation input and resets it in `finally`. It does not persist data itself but controls whether mutating subclasses are allowed to proceed.

Dependencies and integration points: `TransactionInfoRepair` and `UpgradeContainerSchema` inherit this behavior. The class relies on deployment wrappers setting the Ozone service environment variables accurately.

Risks: Service-running detection is environment-variable based and can be false negative. Confirmation reads from stdin, which can block noninteractive use unless `--dry-run` or null service. Dry-run prefixes all messages, including errors. `--force` can permit unsafe mutation while a service is running.

Test signals: Tests should cover dry-run skip, force bypass, running-service refusal, no-service online tools, confirmation accept/reject, formatted messages, and scanner cleanup.
