# UV Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Poetry with `uv`, raise the Python requirement to 3.12, swap `mypy` for `ty`, and leave GitHub Actions workflow filenames unchanged.

**Architecture:** Convert `pyproject.toml` to standard `[project]` metadata with a `dev` dependency group and let `uv` own resolution through `uv.lock`. Keep the existing single-file script layout, make only minimal supporting configuration changes, and verify the migration by syncing and running tests and type checks through `uv`.

**Tech Stack:** Python 3.12, `uv`, `pytest`, `ty`, GitHub Dependabot

---

### Task 1: Convert project metadata

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Replace Poetry metadata with PEP 621 project metadata**

```toml
[project]
name = "handbrake-version-notifier"
version = "0.0.1"
description = "A thing that checks for handbrake versions"
readme = "SECURITY.MD"
requires-python = ">=3.12"
dependencies = [
  "click>=8.3.2",
  "loguru>=0.7.3",
  "requests>=2.33.1",
  "semver>=3.0.4",
]

[dependency-groups]
dev = [
  "black>=26.3.1",
  "pylint>=4.0.5",
  "pytest>=9.0.3",
  "ty>=0.0.1",
  "types-requests>=2.33.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: Verify the file no longer references Poetry**

Run: `rg -n "tool\\.poetry|poetry-core|mypy" pyproject.toml`
Expected: no matches

### Task 2: Regenerate dependency state with uv

**Files:**
- Modify: `uv.lock`
- Delete: `poetry.lock`

- [ ] **Step 1: Remove the Poetry lockfile**

Run: `rm poetry.lock`
Expected: `poetry.lock` is deleted from the worktree

- [ ] **Step 2: Resolve a fresh uv lockfile**

Run: `uv lock --upgrade`
Expected: `uv.lock` contains resolved package entries instead of only header metadata

### Task 3: Update automation metadata

**Files:**
- Modify: `.github/dependabot.yml`

- [ ] **Step 1: Update Dependabot to track the post-migration Python ecosystem**

```yaml
version: 2
updates:
- package-ecosystem: uv
  directory: /
  schedule:
    interval: weekly
    day: saturday
    time: "02:00"
    timezone: "Australia/Brisbane"
- package-ecosystem: github-actions
  directory: /
  schedule:
    interval: weekly
    day: saturday
    time: "02:00"
    timezone: "Australia/Brisbane"
```

- [ ] **Step 2: Confirm workflow filenames are unchanged**

Run: `rg --files .github/workflows`
Expected: existing workflow filenames remain `dependency_review.yml` and `dependabot_auto_merge.yml`

### Task 4: Verify the uv-managed environment

**Files:**
- No direct file edits

- [ ] **Step 1: Sync the environment from the new lockfile**

Run: `uv sync --dev`
Expected: environment installs successfully with Python 3.12-compatible dependencies

- [ ] **Step 2: Run tests**

Run: `uv run pytest -q`
Expected: all tests pass

- [ ] **Step 3: Run type checking**

Run: `uv run ty check`
Expected: no type errors

- [ ] **Step 4: Search for leftover Poetry references**

Run: `rg -n "tool\\.poetry|poetry-core|poetry lock|poetry install|mypy" .`
Expected: no remaining active-project references
