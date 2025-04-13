# Deploying to Homebrew

This document provides instructions for deploying LLMPack to Homebrew using GitHub Actions for automation.

## Prerequisites

1. A GitHub repository for the project (`halst256/llmpack`)
2. A GitHub repository for the Homebrew tap (`halst256/homebrew-tools`)
3. Homebrew installed on your system for testing

## Automated Deployment with GitHub Actions

This project uses GitHub Actions to automatically update the Homebrew formula whenever a new release is published. The workflow performs the following steps:

1. When a new release is published on GitHub, the workflow is triggered
2. The workflow calculates the SHA256 checksum of the release tarball
3. The workflow updates the formula in the Homebrew tap repository
4. Users can then install or update the package using Homebrew

### Setting Up GitHub Actions

1. **Create a Personal Access Token (PAT)**:
   - Go to GitHub's `Settings` > `Developer settings` > `Personal access tokens` > `Tokens (classic)` or `Fine-grained tokens`
   - For `Tokens (classic)`: Select the `repo` scope
   - For `Fine-grained tokens`: Select the `halst256/homebrew-tools` repository and grant `Contents` with `Read and write` permission
   - Copy the generated token (it will only be shown once)

2. **Add the PAT to Repository Secrets**:
   - Go to the `halst256/llmpack` repository on GitHub
   - Navigate to `Settings` > `Secrets and variables` > `Actions`
   - Click `New repository secret`
   - Name: `TAP_REPO_PAT`
   - Value: Paste the PAT you created
   - Click `Add secret`

3. **Create the Homebrew Tap Repository**:
   - Create a new GitHub repository named `homebrew-tools`
   - Clone the repository:
     ```bash
     git clone https://github.com/halst256/homebrew-tools.git
     cd homebrew-tools
     ```
   - Create the Formula directory:
     ```bash
     mkdir -p Formula
     ```
   - Copy the formula file from this repository:
     ```bash
     cp /path/to/llmpack/Formula/llmpack.rb Formula/
     ```
   - Commit and push:
     ```bash
     git add Formula/llmpack.rb
     git commit -m "Add LLMPack formula"
     git push origin main
     ```

## Creating a Release

To create a new release and trigger the automatic formula update:

1. Update the version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # Update to the new version
   ```

2. Commit and push the changes:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.1"
   git push origin main
   ```

3. Create and push a tag:
   ```bash
   git tag -a v0.1.1 -m "Release v0.1.1"
   git push origin v0.1.1
   ```

4. Create a release on GitHub:
   - Go to your repository on GitHub
   - Click on "Releases"
   - Click "Create a new release"
   - Select the tag you just pushed
   - Add release notes
   - Click "Publish release"

5. The GitHub Actions workflow will automatically:
   - Calculate the SHA256 checksum of the release tarball
   - Update the formula in the Homebrew tap repository
   - Commit and push the changes

## Installing from the Tap

Users can install LLMPack using:

```bash
brew tap halst256/tools
brew install llmpack
```

Or directly:

```bash
brew install halst256/tools/llmpack
```

## Updating

Users can update to the latest version with:

```bash
brew update
brew upgrade llmpack
```

## Testing the Formula Locally

Before publishing a release, you can test the formula locally:

```bash
# Test the formula file directly
brew install --build-from-source ./Formula/llmpack.rb

# Or test via the tap
brew tap halst256/tools /path/to/local/homebrew-tools
brew install --build-from-source halst256/tools/llmpack
```
