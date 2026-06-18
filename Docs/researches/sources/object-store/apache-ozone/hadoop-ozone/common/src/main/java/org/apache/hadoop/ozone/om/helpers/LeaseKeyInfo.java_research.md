# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/LeaseKeyInfo.java

Purpose: Small holder tying committed key metadata to open-key metadata for lease recovery or lease inspection operations.

Important APIs/types/functions: Constructor accepts `keyInfo` and `openKeyInfo`; getters expose both `OmKeyInfo` values.

Control flow and state: Immutable references after construction.

State and persistence behavior: No direct persistence. The contained `OmKeyInfo` objects may represent DB values in committed/open key tables.

Dependencies and integration points: Used by OM lease-related code that needs both the visible key and the open-key entry.

Risks: Allows null fields; callers must know which side may be absent.

Test signals: Lease recovery tests should verify the correct committed/open key pair is returned and not swapped.
