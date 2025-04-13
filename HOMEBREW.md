# Deploying to Homebrew

This document provides instructions for deploying LLMPack to Homebrew using GitHub Actions with homebrew-releaser for automation.

## Prerequisites

1. A GitHub repository for the project (`halst256/llmpack`)
2. A GitHub repository for the Homebrew tap (`halst256/homebrew-tools`)
3. Homebrew installed on your system for testing

## Automated Deployment with homebrew-releaser

This project uses [homebrew-releaser](https://github.com/Justintime50/homebrew-releaser) via GitHub Actions to automatically update the Homebrew formula whenever a new release is published. The workflow performs the following steps:

1. When a new release is published on GitHub, the workflow is triggered
2. homebrew-releaser calculates the SHA256 checksum of the release tarball
3. homebrew-releaser generates and updates the formula in the Homebrew tap repository
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

3. **Create the Homebrew Tap Repository** (if not already created):
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
   - Commit and push:
     ```bash
     git add .
     git commit -m "Initialize Homebrew tap"
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

5. The homebrew-releaser GitHub Actions workflow will automatically:
   - Calculate the SHA256 checksum of the release tarball
   - Generate and update the formula in the Homebrew tap repository
   - Commit and push the changes to your tap repository

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

## Homebrew Releaser Configuration

The homebrew-releaser configuration is defined in `.github/workflows/homebrew-release.yml` and includes:

- Automatic formula generation when a new release is published
- Proper dependency management for Python
- Installation and test commands
- Automatic SHA256 checksum calculation
- Automatic commit to the Homebrew tap repository

For more details on the available configuration options, see the [homebrew-releaser documentation](https://github.com/Justintime50/homebrew-releaser).
