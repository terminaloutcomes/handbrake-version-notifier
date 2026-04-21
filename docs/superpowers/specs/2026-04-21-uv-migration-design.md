# UV Migration Design

## Goal

Migrate this repository from Poetry to `uv`, remove Poetry-specific files and configuration entirely, raise the supported Python version to 3.12, and replace `mypy` with `ty`.

## Current State

- Dependency management is defined in `pyproject.toml` under `[tool.poetry]`.
- Locking is still represented by `poetry.lock`.
- An untracked `uv.lock` exists but does not represent a resolved environment yet.
- The repository is a small script-based project rather than a packaged library with a `src/` layout.
- GitHub Actions workflow filenames must remain unchanged.

## Chosen Approach

Convert the project to a simple `uv`-managed application using standard PEP 621 metadata in `pyproject.toml`.

This keeps packaging state in one place, avoids dual-tool ambiguity, and matches the repository's current size and structure. The migration will not add unnecessary package scaffolding or new abstractions.

## Planned Changes

### Project Metadata

- Replace Poetry metadata with `[project]`.
- Set `requires-python = ">=3.12"`.
- Keep the current dependency set unless resolution requires a compatible adjustment.
- Move development tools into a `dev` dependency group.

### Tooling

- Remove `mypy`.
- Add `ty` as the type-checking tool.
- Keep the repository script layout intact.

### Lockfiles

- Delete `poetry.lock`.
- Regenerate `uv.lock` from the converted project definition.

### GitHub Configuration

- Keep existing workflow filenames under `.github/workflows/` unchanged.
- Update dependency-management configuration only where necessary so automated updates continue to work after the migration.

## Dependency Policy

Use `uv` to re-resolve dependencies to reasonably current compatible versions instead of copying Poetry lockfile state forward. The goal is a clean current environment, not perfect continuity with historical pins.

## Verification

- `uv sync` should succeed.
- `uv run pytest` should pass.
- `uv run ty check` should run successfully.
- Repository search should show no remaining Poetry references outside historical git data.
