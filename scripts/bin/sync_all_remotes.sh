#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

current_branch="$(git branch --show-current)"
if [[ -z "${current_branch}" ]]; then
  echo "Not on a branch; aborting." >&2
  exit 1
fi

upstream_remote="$(git config --get "branch.${current_branch}.remote" || true)"
upstream_ref="$(git config --get "branch.${current_branch}.merge" || true)"
if [[ -z "${upstream_remote}" || -z "${upstream_ref}" ]]; then
  echo "No upstream configured for branch ${current_branch}." >&2
  exit 2
fi

target_branch="${upstream_ref#refs/heads/}"

echo "Fetching all remotes..."
git fetch --all --prune

echo "Pulling latest from ${upstream_remote}/${target_branch}..."
git pull --ff-only "${upstream_remote}" "${target_branch}"

echo "Pushing ${current_branch} -> origin/${target_branch}..."
git push origin "HEAD:${target_branch}"

if git remote get-url github >/dev/null 2>&1 && \
  ! git remote get-url --push --all origin | grep -q "github.com/mishrakm/3forge-architecture-diagram.git"; then
  echo "Pushing ${current_branch} -> github/${target_branch}..."
  git push github "HEAD:${target_branch}"
fi

echo "Sync complete for remotes: origin and github"
