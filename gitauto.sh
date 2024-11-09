#!/bin/bash

# Ensure the script is being run from a Git repository or a folder that can be initialized as one
if [ ! -d ".git" ] && [ ! -f ".gitignore" ]; then
    echo "No Git repository found in the current directory. Initializing a new Git repository..."
fi

# Prompt for the repository name or use the current directory name
read -p "Enter the name of the GitHub repository (default: $(basename "$PWD")): " repo_name
repo_name=${repo_name:-$(basename "$PWD")}  # Default to current directory name if empty

# Check if the user is authenticated with GitHub CLI
gh auth status &> /dev/null || { echo "You are not authenticated with GitHub CLI. Please log in using 'gh auth login'"; exit 1; }

# Initialize the repository, add files, commit, create GitHub repository, and push
git init && git add . || { echo "Git operations failed!"; exit 1; }

# Prompt for commit message
read -p "Enter commit message (default: 'Initial commit'): " commit_msg
commit_msg=${commit_msg:-"Initial commit"}
git commit -m "$commit_msg" || { echo "Failed to commit!"; exit 1; }

# Check if the repository already exists on GitHub
gh repo view "$repo_name" &> /dev/null
if [ $? -eq 0 ]; then
    echo "Repository '$repo_name' already exists on GitHub."
    exit 1
fi

# Create the GitHub repository and push to it
gh repo create "$repo_name" --source=. --remote=origin --private --confirm || { echo "Failed to create GitHub repository!"; exit 1; }
git push -u origin main || { echo "Failed to push to GitHub!"; exit 1; }

# Confirmation message
echo "Repository '$repo_name' successfully created on GitHub and changes pushed to the 'main' branch."

