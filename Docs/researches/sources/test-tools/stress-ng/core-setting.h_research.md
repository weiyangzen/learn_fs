# sources/test-tools/stress-ng/core-setting.h

Purpose: defines the typed setting model used to store parsed option values and declares the settings API.

Important APIs/types/functions: `stress_type_id_t` enumerates native numeric, byte-size, percentage, string, boolean, method, and callback setting categories. `stress_setting_t` is a linked-list node containing stressor identity, option name, optional pointer, type id, global flag, current item pointer, and a value union. API declarations cover freeing, showing, debugging, typed set/get, and boolean convenience setters.

Control flow: no runtime logic. The type id determines how implementation copies values, formats output, and converts percentages at lookup.

State and persistence: struct instances are implementation-owned once set. `TYPE_ID_STR` values are dynamically duplicated and freed by the settings subsystem.

Dependencies/integration: depends on `stress_list_item_t`, standard integer/size types, and stress-ng option parsing conventions. Many core modules query settings by string key, so names are integration contracts.

Risks: adding a new type requires updates in set, get, and show code. `TYPE_ID_CALLBACK` exists in the enum but is not actively handled by the current union switch logic.

Test signals: exhaustive switch coverage for enum values, especially byte percent variants and string ownership.
