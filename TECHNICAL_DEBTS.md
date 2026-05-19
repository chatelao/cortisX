# Technical Debts

This file tracks technical debts, outdated components, security flaws, and old patterns discovered in the project.

| Debt | Description | Severity | Status |
|------|-------------|----------|--------|
| Missing CI/CD | Initial project setup lacked an automated pipeline. | Medium | 🚧 Being Addressed |
| Missing Installation Scripts | `src/install.sh` and `test/install.sh` were not initialized. | Low | 🚧 Being Addressed |
| Minimal Project Structure | The `src/` directory only contains a cache folder; lacks core logic modules. | Low | ✅ Resolved |
| Headless 3D Renders | `py3Dmol` export fails in headless environment; using RDKit pseudo-3D instead. | Low | ✅ Resolved |
