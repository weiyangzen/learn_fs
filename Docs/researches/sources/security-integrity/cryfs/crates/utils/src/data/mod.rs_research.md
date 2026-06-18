# sources/security-integrity/cryfs/crates/utils/src/data/mod.rs

Purpose: data module facade.

Important APIs/types/functions: declares `data` and `zeroed`; re-exports `Data` and `ZeroedData`.

Control flow/state: no runtime logic.

Dependencies/integration: gives callers a compact import path for byte buffers and zeroed wrappers.

Risks: any new data submodule needs explicit exposure here if public.

Test signals: child module tests validate behavior.
