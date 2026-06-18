# sources/security-integrity/selinux/gui/domainsPage.py

## Purpose

`domainsPage.py` implements the GUI page for listing SELinux entrypoint domains and toggling per-domain permissive mode.

## Important APIs And Methods

The `domainsPage` class extends `semanagePage`. It uses `sepolicy.get_all_entrypoint_domains()` to seed domain names, `semodule -l` to infer installed permissive modules, and `semanage permissive -a/-d` to add or remove permissive domain modules.

Key methods are `get_modules()`, `load(filter)`, `itemSelected(selection)`, `add()`, `delete()`, and dialog pass-throughs `addDialog()`/`deleteDialog()`.

## Control Flow

Initialization builds a two-column GTK model for domain name and mode, wires filter events and selection changes, stores permissive/enforcing buttons, loads all entrypoint domains, and populates the view. `load()` compares each domain to installed modules named `permissive_<domain>_t` and displays "Permissive" when present. Selection changes enable either the permissive or enforcing button. `add()` runs `semanage permissive -a <domain>_t`; `delete()` runs `semanage permissive -d <domain>_t`.

## State And Persistence

The store reflects current domain permissive status. Persistent state changes are semanage permissive module additions/removals in the SELinux policy store.

## Dependencies And Integration Points

It depends on GTK, `sepolicy`, `semanagePage`, `semodule`, and `semanage`. UI IDs include `domainsFilterEntry`, `permissiveButton`, and `enforcingButton`.

## Risks

`get_modules()` uses `os.popen("semodule -l")` and the add/delete methods build shell command strings. Domain names originate from policy data and are expected to be safe, but shell invocation remains a boundary. Broad `except: pass` in `load()` can hide command or parsing failures. `sort_int` is not relevant here but inherited page behavior may affect selection.

## Test Signals

Tests should mock domain lists and module output to verify permissive detection. Command tests should assert correct semanage calls and button sensitivity transitions for permissive and enforcing states.
