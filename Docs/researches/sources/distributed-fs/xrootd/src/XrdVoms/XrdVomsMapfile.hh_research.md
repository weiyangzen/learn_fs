# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.hh

Purpose: Declares the optional VOMS mapfile singleton and its FQAN mapping API.

Important APIs/types/functions: VOMS_MAP_FAILED is a sentinel pointer for configured-but-failed mapfile setup. Public static Configure() and Get() expose singleton access. Apply(XrdSecEntity &) mutates the entity name when a mapping matches. IsValid() reports last parse validity. Private MapfileEntry stores parsed path and target; private helpers parse, map, compare, make paths, and run maintenance.

Control flow: Configure() should be called during VOMS initialization; Apply() is called after VOMS attributes are populated.

State/persistence: Holds mapfile path, last ctime, shared parsed entries, error destination, validity flag, and static singleton/tried_configure. The mapfile itself is external persistent config.

Dependencies/integration: Includes XrdOucString, XrdSysError, and XrdSecEntity. It integrates XrdVomsFun with site-local username policy.

Risks: Reconfigure() is declared but not defined in the observed source, suggesting dead API or implementation drift. Shared singleton state means only one mapfile per process. Thread-safety of m_is_valid and m_edest updates deserves scrutiny.

Test signals: Header/API tests should assert sentinel handling, singleton reuse, SetErrorStream after prior configure, and Apply() behavior when mapper is null or invalid.
