#!/usr/bin/env bash
branch=${1:-main}

update_submodule() {
    local dir="$1"
    echo -e "\033[1;34m==> Updating submodule: $dir\033[0m"
    (
        cd "$dir" || return
        if git show-ref --verify --quiet "refs/heads/$branch"; then
            git checkout "$branch" && git pull &&
            echo -e "\033[1;32m✔ Successfully updated $dir\033[0m" ||
            echo -e "\033[1;31m✖ Failed to update $dir\033[0m"
        else
            echo -e "\033[1;33m⚠ No branch '$branch' in $dir (skipped)\033[0m"
        fi
    )
}

echo "Starting recursive submodule update from $(pwd)"

# Find all subdirectories containing a .git file (not directory)
find . -type f -name ".git" | while read -r gitfile; do
    submodule_dir=$(dirname "$gitfile")
    update_submodule "$submodule_dir"
done

echo "Finished updating submodules"
